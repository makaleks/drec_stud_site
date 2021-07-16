from loguru import logger
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.commands import CancelAction, ReportProblemStart
from src.keyboards import build_cancel_keyboard, build_keyboard
from src.settings import ADMIN_HARDCODED_LIST, TECHNICAL_ADMIN_ID
from src.states import ReportingStates
from src.utils import is_admin

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(
    text=ReportProblemStart.raw_message_name, state=ReportingStates.DEFAULT
)
async def report_problem_start(message: Message):
    await message.answer(
        message=(await bl.state_dispenser.get(message.peer_id)) is None
    )
    await bl.state_dispenser.set(message.peer_id, ReportingStates.IS_WRITING)
    await message.answer(
        message="Что-то пошло не так?\n"
        "Напиши в свободной форме, я передам это заведующему стиралкой",
        keyboard=build_cancel_keyboard(),
    )
    return True


@bl.labeler.message(state=ReportingStates.IS_WRITING)
async def report_problem_finish(message: Message, **kwargs):
    user_id = message.from_id
    if message.text == CancelAction.button_name:
        await message.answer(
            message="Хорошо, возвращаю в начало",
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )
    else:
        await message.answer(
            message="Отправил это заведующему. Он тебе напишет в ближайшее время.",
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )
        logger.info(
            f"sending problem report from id={user_id} to admins={[ADMIN_HARDCODED_LIST]}"
        )
        await report_to_admin(original_message=message)

    await bl.state_dispenser.set(user_id, ReportingStates.DEFAULT)
    print(bl.state_dispenser)


async def report_to_admin(original_message: Message):
    user = await original_message.get_user()
    await original_message.answer(
        message=f"Проблема у пользователя "
        f"@id{original_message.from_id}({user.first_name + ' ' + user.last_name})."
        f" Вот что пишет:\n{original_message.text}",
        user_id=TECHNICAL_ADMIN_ID,
    )

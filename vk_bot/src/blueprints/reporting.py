from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.commands import CancelAction, ReportProblemStart
from src.keyboards import build_cancel_keyboard, build_keyboard
from src.states import ReportingStates
from src.utils import is_admin

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(
    text=CancelAction.raw_message_name, state=ReportingStates.IS_WRITING
)
async def cancel(message: Message):
    user_id = message.peer_id
    await bl.state_dispenser.delete(user_id)
    await message.answer(
        message="Хорошо, возвращаю в начало",
        keyboard=build_keyboard(is_admin=is_admin(user_id)),
    )


@bl.labeler.message(text=ReportProblemStart.raw_message_name, state=None)
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


@bl.labeler.message(
    state=ReportingStates.IS_WRITING, regexp=f"^{ReportProblemStart.raw_message_name}"
)
async def report_problem_finish(message: Message):
    await message.answer(
        message="Отправил это заведующему. Он тебе напишет в ближайшее время."
    )
    await bl.state_dispenser.delete(message.from_id)

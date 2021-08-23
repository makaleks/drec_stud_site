from loguru import logger
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.commands import CancelAction, GoBackwards, RegistrationStart
from src.keyboards import (
    build_backwards_keyboard,
    build_keyboard,
    build_registration_approve_keyboard,
)
from src.settings import ADMIN_HARDCODED_LIST, TECHNICAL_ADMIN_ID
from src.states import RegistrationStates
from src.utils import is_admin

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(
    text=RegistrationStart.raw_message_name, state=RegistrationStates.DEFAULT
)
@bl.labeler.message(payload={"cmd": RegistrationStart.key})
async def start_registration(message: Message):
    await bl.state_dispenser.set(
        message.peer_id, RegistrationStates.WRITING_GROUP_NUMBER
    )
    await message.answer(
        message="Напиши номер своей группы. Пример: М05-002а, Б04-123, 734",
        keyboard=build_backwards_keyboard(),
    )
    return True


@bl.labeler.message(state=RegistrationStates.WRITING_GROUP_NUMBER)
async def process_group_entry(message: Message, **kwargs):
    user_id = message.from_id
    if message.text == GoBackwards.button_name:
        await bl.state_dispenser.set(user_id, RegistrationStates.DEFAULT)
        await message.answer(
            message="Хорошо, возвращаю назад",
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )
    else:
        await bl.state_dispenser.set(user_id, RegistrationStates.WRITING_ROOM_NUMBER)
        await message.answer(
            message="Хорошо, принял. Какой у тебя номер комнаты?",
            keyboard=build_backwards_keyboard(),
        )
    print(bl.state_dispenser)


@bl.labeler.message(state=RegistrationStates.WRITING_ROOM_NUMBER)
async def process_room_entry(message: Message, **kwargs):
    user_id = message.from_id
    if message.text == GoBackwards.button_name:
        await bl.state_dispenser.set(user_id, RegistrationStates.WRITING_GROUP_NUMBER)
        await message.answer(
            message="Хорошо, возвращаю назад",
            keyboard=build_backwards_keyboard(),
        )
    else:
        await bl.state_dispenser.set(user_id, RegistrationStates.APPROVING_INPUT)
        name, surname, group, room_number = "Ололош", "Ололошев", "321", "123-1"
        await message.answer(
            message="Итак, вот данные для регистрации. Имя и фамилию я взял из ВК."
            "\n\n"
            f"Имя: {name}\n"
            f"Фамилия: {surname}\n"
            f"Группа: {group}\n"
            f"Номер комнаты: {room_number}"
            "\n\n"
            "Все верно?",
            keyboard=build_registration_approve_keyboard(),
        )


@bl.labeler.message(state=RegistrationStates.APPROVING_INPUT)
async def registration_finish(message: Message, **kwargs):
    user_id = message.from_id
    if message.text == GoBackwards.button_name:
        await bl.state_dispenser.set(user_id, RegistrationStates.WRITING_ROOM_NUMBER)
        await message.answer(
            message="Хорошо, возвращаю назад",
            keyboard=build_backwards_keyboard(),
        )
    else:
        await bl.state_dispenser.set(user_id, RegistrationStates.DEFAULT)
        await message.answer(
            message="Зарегистрировал тебя в стиралку. "
            'Теперь можно зайти в https://8ka.mipt.ru и нажать кнопку "Войти через ВК".',
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )

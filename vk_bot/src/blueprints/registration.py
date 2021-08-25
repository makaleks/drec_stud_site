import json
import os

import aiohttp
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


async def is_registered(user_id: int) -> bool:
    return False


@bl.labeler.message(
    text=RegistrationStart.raw_message_name, state=RegistrationStates.DEFAULT
)
@bl.labeler.message(payload={"cmd": RegistrationStart.key})
async def start_registration(message: Message):
    user_id = message.from_id
    if await is_registered(user_id):
        logger.info(f"{message.from_id}: user is already registered, rejecting")
        await message.answer(
            message="Насколько я вижу, ты уже зарегистрирован в стиралке. Возврат в начало",
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )
        return True
    await bl.state_dispenser.set(
        message.peer_id, RegistrationStates.WRITING_GROUP_NUMBER
    )
    logger.info(f"{message.from_id}: entering group number")
    await message.answer(
        message="Напиши номер своей группы. Пример: М05-002а, Б04-123, 734",
        keyboard=build_backwards_keyboard(),
    )
    return True


@bl.labeler.message(state=RegistrationStates.WRITING_GROUP_NUMBER)
async def process_group_entry(message: Message, **kwargs):
    user_id = message.from_id
    group_number = message.text
    if message.text == GoBackwards.button_name:
        await bl.state_dispenser.set(user_id, RegistrationStates.DEFAULT)
        logger.info(f"{message.from_id}: back to default state")
        await message.answer(
            message="Хорошо, возвращаю в начало",
            keyboard=build_keyboard(is_admin=is_admin(user_id)),
        )
    else:
        await bl.state_dispenser.set(
            user_id,
            RegistrationStates.WRITING_ROOM_NUMBER,
            group_number=group_number,
        )
        logger.info(f"{message.from_id}: entering room number")
        await message.answer(
            message="Какой у тебя номер комнаты?",
            keyboard=build_backwards_keyboard(),
        )
    print(bl.state_dispenser)


@bl.labeler.message(state=RegistrationStates.WRITING_ROOM_NUMBER)
async def process_room_entry(message: Message, **kwargs):
    user_id = message.from_id
    room_number = message.text
    if message.text == GoBackwards.button_name:
        await bl.state_dispenser.set(user_id, RegistrationStates.WRITING_GROUP_NUMBER)
        logger.info(f"{message.from_id}: back to WRITING_GROUP_NUMBER")
        await message.answer(
            message="Хорошо, возвращаю назад.",
            keyboard=build_backwards_keyboard(),
        )
        await message.answer(
            message="Напиши номер своей группы. Пример: М04-002а, Б04-123, 734",
            keyboard=build_backwards_keyboard(),
        )
    else:
        await bl.state_dispenser.set(
            user_id, RegistrationStates.APPROVING_INPUT, room_number=room_number
        )
        logger.info(f"{message.from_id}: approving input")
        user = await message.get_user()
        name, surname, group, room_number = (
            user.first_name,
            user.last_name,
            message.state_peer.payload["group_number"],
            room_number,
        )
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
        logger.info(f"{message.from_id}: back to WRITING_ROOM_NUMBER")
        await message.answer(
            message="Хорошо, возвращаю назад",
            keyboard=build_backwards_keyboard(),
        )
        await message.answer(
            message="Какой у тебя номер комнаты?",
            keyboard=build_backwards_keyboard(),
        )
    else:
        await bl.state_dispenser.set(user_id, RegistrationStates.DEFAULT)
        # Get info
        logger.info(
            f"{message.from_id}: getting user data before finishing registration"
        )
        user = await message.get_user()
        name, surname, group, room_number = (
            user.first_name,
            user.last_name,
            message.state_peer.payload["group_number"],
            message.state_peer.payload["room_number"],
        )
        # Send registration request to the website
        logger.info(f"{message.from_id}: sending registration request to backend")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{os.environ["STIRKA_SITE"]}/user/register',
                json={
                    "token": os.environ["STIRKA_REGISTRATION_TOKEN"],
                    "account_id": user_id,
                    "last_name": surname,
                    "first_name": name,
                    "room_number": room_number,
                    "group_number": group,
                },
            ) as response:
                error = None
                try:
                    resp_text = await response.text()
                    logger.info(
                        f"got response status {response.status} and text: {resp_text}"
                    )
                    resp_json = json.loads(resp_text)
                    if resp_json.get("status") != "ok":
                        error = resp_json
                except Exception as e:
                    error = e
                if error is not None:
                    if isinstance(error, dict) and error.get("status") == "fail":
                        logger.info(f"{message.from_id}: user input problem: {error}")
                        await message.answer(
                            message=f"Кажется, ошибка в вводе данных: {error.get('error')}\n\n"
                            f"Проверь данные и попробуй зарегистрироваться еще раз. "
                            f"Если совсем ничего не получается, пиши @id{TECHNICAL_ADMIN_ID}",
                            keyboard=build_keyboard(is_admin=is_admin(user_id)),
                        )

                    else:
                        logger.error(
                            f"{message.from_id}: failed to register with error: {error}"
                        )
                        await message.answer(
                            message=f"Что-то пошло не так, и я не понимаю, как это случилось. "
                            f"Не ругайся, я только учусь!\n\n"
                            f"Напиши @id{TECHNICAL_ADMIN_ID} об этом",
                            keyboard=build_keyboard(is_admin(user_id)),
                        )
                else:
                    logger.info(f"{message.from_id}: successfully registered")
                    await message.answer(
                        message="Зарегистрировал тебя в стиралку. "
                        'Теперь можно зайти в https://8ka.mipt.ru и нажать кнопку "Войти через ВК".',
                        keyboard=build_keyboard(is_admin=is_admin(user_id)),
                    )

import os
from typing import Union
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from vkbottle_types import BaseStateGroup
from loguru import logger
from src.keyboards import KEYBOARD_ENTRYPOINT
from src.settings import TECHNICAL_ADMIN_ID
from src.commands import AdminOpenLock, AdminCloseLock
from src.lockbox_api import send_signal_door_open, send_signal_door_close

ADMIN_HARDCODED_LIST = [
    TECHNICAL_ADMIN_ID,
    94592201
]


class AdminDoorControlStates(BaseStateGroup):
    CLOSED = 0
    OPENED = 1


class MyRule(rules.ABCMessageRule):
    async def check(self, message: Message) -> Union[dict, bool]:
        token = os.environ.get('SECRET_BOT_TOKEN')
        if token is None:
            logger.warning('failure in token read')
            await message.answer(
                message='Мне не удалось считать токен, поэтому я не смогу управлять замком. Возврат в меню',
                keyboard=KEYBOARD_ENTRYPOINT
            )
            return False
        return True


bl = BotBlueprint()
bl.labeler.auto_rules = [
    rules.PeerRule(from_chat=False),
    rules.FromPeerRule(ADMIN_HARDCODED_LIST),
    MyRule()
]


@bl.labeler.message(command=AdminOpenLock.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminOpenLock.key})
async def handle_open_door_request(message: Message, **kwargs):
    state = await bl.state_dispenser.get(message.peer_id)
    if state and state.state == AdminDoorControlStates.OPENED:
        await message.answer(
            message='Уже был запрос на открытие двери. Возврат',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    try:
        status, content_text = await send_signal_door_open(room_name='5b')
    except Exception as e:
        logger.error(f'Unknown error: {e}')
        await message.answer(
            message='Произошла неизвестная ошибка, '
                    'но разработчики смогут о ней узнать',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    if status != 200:
        logger.warning(f'response is invalid | status = {status} | content={content_text}')
        await message.answer(
            message=f'Запрос вернул status_code={status} != 200, так не должно быть. '
                    f'Вот контент: {content_text}',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    else:
        await bl.state_dispenser.set(message.peer_id, AdminDoorControlStates.OPENED)
        await message.answer(
            message='Дверь в 5Б должна быть открыта.',
            keyboard=KEYBOARD_ENTRYPOINT
        )


@bl.labeler.message(command=AdminCloseLock.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminCloseLock.key})
async def handle_close_door_request(message: Message, **kwargs):
    state = await bl.state_dispenser.get(message.peer_id)
    if state and state.state == AdminDoorControlStates.CLOSED:
        await message.answer(
            message='Уже был запрос на закрытие двери. Возврат',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    try:
        status, content_text = await send_signal_door_close(room_name='5b')
    except Exception as e:
        logger.error(f'Unknown error: {e}')
        await message.answer(
            message='Произошла неизвестная ошибка, '
                    'но разработчики смогут о ней узнать',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    if status != 200:
        logger.warning(f'response is invalid | status = {status} | content={content_text}')
        await message.answer(
            message=f'Запрос вернул status_code={status} != 200, так не должно быть. '
                    f'Вот контент: {content_text}',
            keyboard=KEYBOARD_ENTRYPOINT
        )
        return
    else:
        await bl.state_dispenser.set(message.peer_id, AdminDoorControlStates.CLOSED)
        await message.answer(
            message='Дверь в 5Б должна быть закрыта.',
            keyboard=KEYBOARD_ENTRYPOINT
        )
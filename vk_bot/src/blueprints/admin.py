import os
from typing import Union
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from vkbottle_types import BaseStateGroup
from loguru import logger
from src.keyboards import KEYBOARD_ENTRYPOINT
from src.settings import ADMIN_HARDCODED_LIST
from src.commands import AdminOpenLock5, AdminCloseLock5, AdminOpenLock6, AdminCloseLock6
from src.lockbox_api import send_signal_door_open, send_signal_door_close


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


async def process_door_command(message: Message, room_id: str, display_room_name: str, do_open: bool):
    try:
        status, content_text = await (
            send_signal_door_open(room_name=room_id) if do_open
            else send_signal_door_close(room_name=room_id)
        )
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
        await message.answer(
            message=f'Дверь в {display_room_name} должна быть {"открыта" if do_open else "закрыта"}.',
            keyboard=KEYBOARD_ENTRYPOINT
        )


@bl.labeler.message(command=AdminOpenLock5.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminOpenLock5.key})
async def handle_open_5b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='5b', display_room_name='5Б', do_open=True)


@bl.labeler.message(command=AdminOpenLock6.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminOpenLock6.key})
async def handle_open_6b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='6b', display_room_name='6Б', do_open=True)


@bl.labeler.message(command=AdminCloseLock5.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminCloseLock5.key})
async def handle_close_5b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='5b', display_room_name='5Б', do_open=False)


@bl.labeler.message(command=AdminCloseLock6.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminCloseLock6.key})
async def handle_close_6b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='6b', display_room_name='6Б', do_open=False)

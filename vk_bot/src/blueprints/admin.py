from loguru import logger
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from src.settings import ADMIN_HARDCODED_LIST
from src.commands import AdminCloseLock5, AdminCloseLock6
from src.utils import process_door_command, LockboxTokenIsPresentRule


bl = BotBlueprint()
bl.labeler.auto_rules = [
    rules.PeerRule(from_chat=False),
    rules.FromPeerRule(peer_ids=ADMIN_HARDCODED_LIST),
    LockboxTokenIsPresentRule()
]


@bl.labeler.message(command=AdminCloseLock5.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminCloseLock5.key})
async def handle_close_5b(message: Message, **kwargs):
    logger.info(f'close request for 5b from {message.from_id}')
    await process_door_command(message=message, room_id='5b', display_room_name='5Б', do_open=False)


@bl.labeler.message(command=AdminCloseLock6.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminCloseLock6.key})
async def handle_close_6b(message: Message, **kwargs):
    logger.info(f'close request for 6b from {message.from_id}')
    await process_door_command(message=message, room_id='6b', display_room_name='6Б', do_open=False)

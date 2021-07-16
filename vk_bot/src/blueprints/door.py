from loguru import logger
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.commands import AdminOpenLock5, AdminOpenLock6
from src.utils import LockboxTokenIsPresentRule, process_door_command

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False), LockboxTokenIsPresentRule()]


@bl.labeler.message(text=AdminOpenLock5.raw_message_name)
@bl.labeler.message(payload={"cmd": AdminOpenLock5.key})
async def handle_open_5b(message: Message, **kwargs):
    logger.info(f"open request for 5b from {message.from_id}")
    await process_door_command(
        message=message, room_id="5b", display_room_name="5Б", do_open=True
    )


@bl.labeler.message(text=AdminOpenLock6.raw_message_name)
@bl.labeler.message(payload={"cmd": AdminOpenLock6.key})
async def handle_open_6b(message: Message, **kwargs):
    logger.info(f"open request for 6b from {message.from_id}")
    await process_door_command(
        message=message, room_id="6b", display_room_name="6Б", do_open=True
    )

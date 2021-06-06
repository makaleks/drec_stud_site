from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from src.commands import AdminOpenLock5, AdminOpenLock6
from src.utils import process_door_command, LockboxTokenIsPresentRule


bl = BotBlueprint()
bl.labeler.auto_rules = [
    rules.PeerRule(from_chat=False),
    LockboxTokenIsPresentRule()
]


@bl.labeler.message(command=AdminOpenLock5.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminOpenLock5.key})
async def handle_open_5b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='5b', display_room_name='5Б', do_open=True)


@bl.labeler.message(command=AdminOpenLock6.raw_message_name)
@bl.labeler.message(payload={'cmd': AdminOpenLock6.key})
async def handle_open_6b(message: Message, **kwargs):
    await process_door_command(message=message, room_id='6b', display_room_name='6Б', do_open=True)

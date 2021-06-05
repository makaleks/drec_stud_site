from vkbottle import Keyboard, KeyboardButtonColor, Text
from src.commands import *


KEYBOARD_ENTRYPOINT = Keyboard(inline=False, one_time=True)
KEYBOARD_ENTRYPOINT.add(
    Text(AdminOpenLock5.button_name, payload={'cmd': AdminOpenLock5.key}), color=KeyboardButtonColor.PRIMARY
)

KEYBOARD_ENTRYPOINT.add(
    Text(AdminCloseLock5.button_name, payload={'cmd': AdminCloseLock5.key}), color=KeyboardButtonColor.PRIMARY
)
KEYBOARD_ENTRYPOINT.row()
KEYBOARD_ENTRYPOINT.add(
    Text(AdminOpenLock6.button_name, payload={'cmd': AdminOpenLock6.key}), color=KeyboardButtonColor.PRIMARY
)
KEYBOARD_ENTRYPOINT.add(
    Text(AdminCloseLock6.button_name, payload={'cmd': AdminCloseLock6.key}), color=KeyboardButtonColor.PRIMARY
)
KEYBOARD_ENTRYPOINT.row()

for command in [GetPasswordCommand, HelpCommand]:
    KEYBOARD_ENTRYPOINT.add(
        Text(command.button_name, payload={'cmd': command.key}),
        color=KeyboardButtonColor.SECONDARY
    )

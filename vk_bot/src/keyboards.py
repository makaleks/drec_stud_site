from vkbottle import Keyboard, KeyboardButtonColor, Text

from src.commands import *


def build_keyboard(is_admin: bool = False):
    keyboard = Keyboard(inline=False, one_time=True)
    keyboard.add(
        Text(AdminOpenLock5.button_name, payload={"cmd": AdminOpenLock5.key}),
        color=KeyboardButtonColor.PRIMARY,
    )
    keyboard.add(
        Text(AdminOpenLock6.button_name, payload={"cmd": AdminOpenLock6.key}),
        color=KeyboardButtonColor.PRIMARY,
    )
    keyboard.row()
    if is_admin:
        keyboard.add(
            Text(AdminCloseLock5.button_name, payload={"cmd": AdminCloseLock5.key}),
            color=KeyboardButtonColor.PRIMARY,
        )
        keyboard.add(
            Text(AdminCloseLock6.button_name, payload={"cmd": AdminCloseLock6.key}),
            color=KeyboardButtonColor.PRIMARY,
        )
        keyboard.row()

    for command in [GetPasswordCommand, HelpCommand]:
        keyboard.add(
            Text(command.button_name, payload={"cmd": command.key}),
            color=KeyboardButtonColor.SECONDARY,
        )
    return keyboard


def build_cancel_keyboard():
    """Клавиатура с единственной кнопкой 'Отмена'."""
    keyboard = Keyboard(inline=False, one_time=True)
    keyboard.add(
        Text(CancelAction.button_name, payload={"cmd": CancelAction.key}),
        color=KeyboardButtonColor.SECONDARY,
    )
    return keyboard

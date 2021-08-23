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

    keyboard.add(
        Text(RegistrationStart.button_name, payload={"cmd": RegistrationStart.key}),
        color=KeyboardButtonColor.SECONDARY,
    )
    keyboard.row()

    for command in [GetPasswordCommand, HelpCommand]:
        keyboard.add(
            Text(command.button_name, payload={"cmd": command.key}),
            color=KeyboardButtonColor.SECONDARY,
        )
    # TODO: тест на клавиатуру
    keyboard.row()
    keyboard.add(
        Text(ReportProblemStart.button_name, payload={"cmd": ReportProblemStart.key}),
        color=KeyboardButtonColor.PRIMARY,
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


def build_backwards_keyboard(keyboard=None):
    """Клавиатура с единственной кнопкой 'Назад'."""
    if keyboard is None:
        keyboard = Keyboard(inline=False, one_time=True)
    keyboard.add(
        Text(GoBackwards.button_name, payload={"cmd": GoBackwards.key}),
        color=KeyboardButtonColor.SECONDARY,
    )
    return keyboard


def build_registration_approve_keyboard(keyboard=None):
    if keyboard is None:
        keyboard = Keyboard(inline=False, one_time=True)
    keyboard.add(
        Text(
            RegistrationDataCorrect.button_name,
            payload={"cmd": RegistrationDataCorrect.key},
        ),
        color=KeyboardButtonColor.PRIMARY,
    )
    keyboard.row()
    keyboard = build_backwards_keyboard(keyboard)
    return keyboard

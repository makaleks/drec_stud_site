class CommandBase:
    key: str
    raw_message_name: str
    button_name: str
    description: str


class HelpCommand(CommandBase):
    key = 'help'
    raw_message_name = 'помощь'
    button_name = 'Помощь'
    description = 'Напечатать список всех команд'


class GetPasswordCommand(CommandBase):
    key = 'get_password'
    raw_message_name = 'пароль'
    button_name = 'Мой пароль'
    description = 'Получить логин и пароль для экстренной авторизации'


class AdminOpenLock(CommandBase):
    key = 'open_lock_5b'
    raw_message_name = 'открыть_5Б'
    button_name = 'Открыть 5Б'
    description = '(ТОЛЬКО АДМИНАМ) Открыть замок 5Б'

class AdminCloseLock(CommandBase):
    key = 'close_lock_5b'
    raw_message_name = 'закрыть_5Б'
    button_name = 'Закрыть 5Б'
    description = '(ТОЛЬКО АДМИНАМ) Закрыть замок 5Б'


available_commands = [AdminOpenLock, AdminCloseLock, HelpCommand, GetPasswordCommand]

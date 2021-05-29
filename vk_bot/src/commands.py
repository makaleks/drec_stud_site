class CommandBase:
    """
    Базовый класс, по которому строятся команды
    """
    key: str                # внутренний id-шник, должен быть уникален
    raw_message_name: str   # что печатать пользователю, чтобы достучаться до этой команды
    button_name: str        # Текст в кнопке
    description: str        # Описание, которое отдаст "Помощь"


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

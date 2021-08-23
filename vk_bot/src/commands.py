class CommandBase:
    """Базовый класс, по которому строятся команды."""

    key: str  # внутренний id-шник, должен быть уникален
    raw_message_name: str  # что печатать пользователю, чтобы достучаться до этой команды
    button_name: str  # Текст в кнопке
    description: str  # Описание, которое отдаст "Помощь"


class HelpCommand(CommandBase):
    key = "help"
    raw_message_name = "помощь"
    button_name = "Помощь"
    description = "Напечатать список всех команд"


class GetPasswordCommand(CommandBase):
    key = "get_password"
    raw_message_name = "пароль"
    button_name = "Мой пароль"
    description = "Получить логин и пароль для экстренной авторизации"


class AdminOpenLock5(CommandBase):
    key = "open_lock_5b"
    raw_message_name = "открыть_5Б"
    button_name = "Открыть 5Б"
    description = "Открыть замок 5Б"


class AdminCloseLock5(CommandBase):
    key = "close_lock_5b"
    raw_message_name = "закрыть_5Б"
    button_name = "Закрыть 5Б"
    description = "(ТОЛЬКО АДМИНАМ) Закрыть замок 5Б"


class AdminOpenLock6(CommandBase):
    key = "open_lock_6b"
    raw_message_name = "открыть_6Б"
    button_name = "Открыть 6Б"
    description = "Открыть замок 6Б"


class AdminCloseLock6(CommandBase):
    key = "close_lock_6b"
    raw_message_name = "закрыть_6Б"
    button_name = "Закрыть 6Б"
    description = "(ТОЛЬКО АДМИНАМ) Закрыть замок 6Б"


class ReportProblemStart(CommandBase):
    key = "report_problem"
    raw_message_name = "проблема"
    button_name = "Есть проблема"
    description = "Доложить о проблеме в стиралке"


class CancelAction(CommandBase):
    key = "cancel"
    raw_message_name = "отмена"
    button_name = "Отмена"
    description = "Отменить действие"


class GoBackwards(CommandBase):
    key = "backwards"
    raw_message_name = "назад"
    button_name = "Назад"
    description = "К предыдущему выбору"


class RegistrationStart(CommandBase):
    key = "register_user"
    raw_message_name = "зарегистрироваться"
    button_name = "Я новый пользователь"
    description = "Регистрация на сайте через ВК"


class RegistrationDataCorrect(CommandBase):
    key = "registration_data_correct"
    raw_message_name = "данные_верны"
    button_name = "Да, все верно"
    description = "Подтвердить правильность данных регистрации"


regular_commands = [
    AdminOpenLock5,
    AdminOpenLock6,
    HelpCommand,
    GetPasswordCommand,
    ReportProblemStart,
]

admin_commands = [
    AdminCloseLock5,
    AdminCloseLock6,
]

from pytest_cases import case, parametrize

from src.blueprints.admin import handle_close_5b, handle_close_6b
from src.blueprints.defaults import hello_admin
from src.blueprints.door import handle_open_5b, handle_open_6b
from src.blueprints.emergency_password import send_emergency_password
from src.blueprints.help import print_help
from src.commands import (
    AdminCloseLock5,
    AdminCloseLock6,
    AdminOpenLock5,
    AdminOpenLock6,
    GetPasswordCommand,
    HelpCommand,
)
from src.settings import ADMIN_HARDCODED_LIST


@case(tags="from_admin")
@parametrize(**{"from_id": ADMIN_HARDCODED_LIST})
class AdminCases:
    def case_open_5b(
        self,
        from_id,
    ):
        # text, id, handler_function
        return AdminOpenLock5.raw_message_name, from_id, handle_open_5b

    def case_open_6b(
        self,
        from_id,
    ):
        # text, id, handler_function
        return AdminOpenLock6.raw_message_name, from_id, handle_open_6b

    def case_close_5b(
        self,
        from_id,
    ):
        # text, id, handler_function
        return (
            AdminCloseLock5.raw_message_name,
            from_id,
            handle_close_5b,
        )

    def case_close_6b(
        self,
        from_id,
    ):
        # text, id, handler_function
        return (
            AdminCloseLock6.raw_message_name,
            from_id,
            handle_close_6b,
        )

    @parametrize(**{"text": ["command fialw", "фывйцв", "smtgsh"]})
    def case_unknown_message(
        self,
        text,
        from_id,
    ):
        return text, from_id, hello_admin

    def case_help_message(
        self,
        from_id,
    ):
        return HelpCommand.raw_message_name, from_id, print_help

    def case_password_message(
        self,
        from_id,
    ):
        return (
            GetPasswordCommand.raw_message_name,
            from_id,
            send_emergency_password,
        )


# Проверка на то, что на запретной команде сваливается в `hello_admin`
@case(tags="from_nonadmin")
@parametrize(
    **{
        "from_id": [188477847],
        # Сюда пишите команды, которые запрещены обычным пользователям
        "command": [AdminCloseLock5, AdminCloseLock6],
    }
)
class RestrictedCommandsCases:
    def case_forbidden_command(self, from_id, command):
        # text, id, handler_function
        return command.raw_message_name, from_id, hello_admin

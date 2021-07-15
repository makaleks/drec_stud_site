from pytest_cases import case, parametrize

from src.blueprints.admin import handle_close_5b, handle_close_6b
from src.blueprints.defaults import hello_admin
from src.blueprints.door import handle_open_5b, handle_open_6b
from src.blueprints.emergency_password import send_emergency_password
from src.blueprints.help import print_help
from src.blueprints.reporting import report_problem_start
from src.commands import (
    AdminCloseLock5,
    AdminCloseLock6,
    AdminOpenLock5,
    AdminOpenLock6,
    GetPasswordCommand,
    HelpCommand,
    ReportProblemStart,
)
from src.settings import ADMIN_HARDCODED_LIST


@case(tags="from_admin")
@parametrize(**{"from_id": ADMIN_HARDCODED_LIST, "command_prefix": ["!", "/"]})
class AdminCases:
    def case_open_5b(self, from_id, command_prefix):
        # text, id, handler_function
        return command_prefix + AdminOpenLock5.raw_message_name, from_id, handle_open_5b

    def case_open_6b(self, from_id, command_prefix):
        # text, id, handler_function
        return command_prefix + AdminOpenLock6.raw_message_name, from_id, handle_open_6b

    def case_close_5b(self, from_id, command_prefix):
        # text, id, handler_function
        return (
            command_prefix + AdminCloseLock5.raw_message_name,
            from_id,
            handle_close_5b,
        )

    def case_close_6b(self, from_id, command_prefix):
        # text, id, handler_function
        return (
            command_prefix + AdminCloseLock6.raw_message_name,
            from_id,
            handle_close_6b,
        )

    @parametrize(**{"text": ["command fialw", "фывйцв", "smtgsh"]})
    def case_unknown_message(self, text, from_id, command_prefix):
        return text, from_id, hello_admin

    def case_help_message(self, from_id, command_prefix):
        return command_prefix + HelpCommand.raw_message_name, from_id, print_help

    def case_password_message(self, from_id, command_prefix):
        return (
            command_prefix + GetPasswordCommand.raw_message_name,
            from_id,
            send_emergency_password,
        )

    def case_report_problem(self, from_id, command_prefix):
        return (
            command_prefix + ReportProblemStart.raw_message_name,
            from_id,
            report_problem_start,
        )


# Проверка на то, что на запретной команде сваливается в `hello_admin`
@case(tags="from_nonadmin")
@parametrize(
    **{
        "from_id": [188477847],
        "command_prefix": ["!", "/"],
        # Сюда пишите команды, которые запрещены обычным пользователям
        "command": [AdminCloseLock5, AdminCloseLock6],
    }
)
class RestrictedCommandsCases:
    def case_forbidden_command(self, from_id, command_prefix, command):
        # text, id, handler_function
        return command_prefix + command.raw_message_name, from_id, hello_admin

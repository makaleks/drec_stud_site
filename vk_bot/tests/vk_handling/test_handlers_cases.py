from pytest_cases import case, parametrize
from src.commands import AdminOpenLock5, AdminOpenLock6, AdminCloseLock5, AdminCloseLock6
from src.blueprints.admin import handle_open_5b, handle_open_6b, handle_close_5b, handle_close_6b
from src.blueprints.defaults import hello_admin
from src.blueprints.help import print_help
from src.blueprints.emergency_password import send_emergency_password
from src.settings import TECHNICAL_ADMIN_ID


@case(tags='from_admin')
class DoorControlCases:
    def case_open_5b(self):
        # text, id, handler_function
        return '!' + AdminOpenLock5.raw_message_name, TECHNICAL_ADMIN_ID, handle_open_5b

    def case_open_6b(self):
        # text, id, handler_function
        return '!' + AdminOpenLock6.raw_message_name, TECHNICAL_ADMIN_ID, handle_open_6b

    def case_close_5b(self):
        # text, id, handler_function
        return '!' + AdminCloseLock5.raw_message_name, TECHNICAL_ADMIN_ID, handle_close_5b

    def case_close_6b(self):
        # text, id, handler_function
        return '!' + AdminCloseLock6.raw_message_name, TECHNICAL_ADMIN_ID, handle_close_6b


@parametrize('text', [
    'command fialw', 'фывйцв', 'smtgsh'
])
def case_unknown_message(text):
    return text, TECHNICAL_ADMIN_ID, hello_admin


@parametrize('text', [
    '!помощь', '/помощь'
])
def case_help_message(text):
    return text, TECHNICAL_ADMIN_ID, print_help


@parametrize('text', [
    '!пароль', '/пароль'
])
def case_password_message(text):
    return text, TECHNICAL_ADMIN_ID, send_emergency_password

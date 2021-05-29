from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from src.keyboards import KEYBOARD_ENTRYPOINT
from src.commands import HelpCommand, available_commands


bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(command=HelpCommand.raw_message_name)
@bl.labeler.message(payload={'cmd': HelpCommand.key})
async def print_help(message: Message, **kwargs):
    help_message = (
        'Это бот стиралки. '
        'Пока он умеет не очень много, но со временем список пополнится.'
        '\n'
        'Ты можешь писать команды в формате \"/команда\", например, \"/помощь\". '
        'Или можешь использовать кнопки внизу :)'
        '\n'
        '\n'
        'Вот что я пока умею:'
        '\n'
    )
    help_message += '\n'.join([f"/{x.raw_message_name} (кнопка \"{x.button_name}\") - {x.description}"
                               for x in available_commands])
    await message.answer(message=help_message, keyboard=KEYBOARD_ENTRYPOINT)

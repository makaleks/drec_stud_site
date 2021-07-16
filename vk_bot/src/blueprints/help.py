from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.commands import HelpCommand, admin_commands, regular_commands
from src.keyboards import build_keyboard
from src.utils import is_admin

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(text=HelpCommand.raw_message_name)
@bl.labeler.message(payload={"cmd": HelpCommand.key})
async def print_help(message: Message, **kwargs):
    help_message = (
        "Это бот стиралки. "
        "Пока он умеет не очень много, но со временем список пополнится."
        "\n"
        'Ты можешь писать команды в формате "команда", например, "помощь". '
        "Или можешь использовать кнопки внизу :)"
        "\n"
        "\n"
        "Вот что я пока умею:"
        "\n"
    )
    help_message += "\n".join(
        [
            f'{x.raw_message_name} (кнопка "{x.button_name}") - {x.description}'
            for x in regular_commands
        ]
    )
    if is_admin(message.from_id):
        help_message += "\n\nТак как ты админ, тебе доступны дополнительные команды:\n"
        help_message += "\n".join(
            [
                f'{x.raw_message_name} (кнопка "{x.button_name}") - {x.description}'
                for x in admin_commands
            ]
        )
    await message.answer(
        message=help_message,
        keyboard=build_keyboard(is_admin=is_admin(message.from_id)),
    )

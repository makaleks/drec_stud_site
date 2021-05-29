from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from src.keyboards import KEYBOARD_ENTRYPOINT


bl = BotBlueprint(name='default')
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message()
async def hello_admin(message: Message, **kwargs):
    await message.answer(
        message='Либо я не понял команду, либо у тебя нет на нее прав доступа. '
                'Можешь повторить еще раз из списка?',
        keyboard=KEYBOARD_ENTRYPOINT
    )

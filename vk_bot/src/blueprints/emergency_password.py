import aioredis
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules
from src.redis_.crud import get_password_from_redis
from src.keyboards import KEYBOARD_ENTRYPOINT
from src.settings import TECHNICAL_ADMIN_ID
from src.commands import GetPasswordCommand

bl = BotBlueprint()
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(command=GetPasswordCommand.raw_message_name)
@bl.labeler.message(payload={'cmd': GetPasswordCommand.key})
async def send_emergency_password(message: Message, redis: aioredis.Redis):
    user_id = message.from_id
    password = await get_password_from_redis(redis, user_id=user_id)
    if not password:
        answer = f"Не получилось найти. Напиши @id{TECHNICAL_ADMIN_ID} (сюда) об этом"
    else:
        answer = f"Логин: {user_id}\n" \
             f"Пароль: {await get_password_from_redis(redis, user_id=user_id)}\n\n" \
             f"Что-то еще?"
    await message.answer(message=answer, keyboard=KEYBOARD_ENTRYPOINT)

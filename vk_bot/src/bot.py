import os
import sys
from loguru import logger

from vkbottle import load_blueprints_from_package
from vkbottle.bot import Bot
from dotenv import load_dotenv
from src.middlewares import RedisMiddleware

load_dotenv('../.env')
TOKEN = os.environ.get('ACCESS_TOKEN')

bot = Bot(TOKEN)

logger.remove()
logger.add(sys.stderr, level="DEBUG")


bp_default = None
for bp in load_blueprints_from_package('blueprints'):
    if not bp.name == 'default':
        bp.load(bot)
    else:
        bp_default = bp
else:
    if bp_default:
        bp_default.load(bot)


bot.labeler.message_view.register_middleware(RedisMiddleware)


if __name__ == '__main__':
    bot.run_forever()

from aioredis import Redis
from vkbottle import BaseMiddleware
from vkbottle.tools.dev_tools.mini_types.bot.message import MessageMin
from loguru import logger

from src.redis_.crud import get_redis
from src.commands import GetPasswordCommand
from src.utils import get_event_payload_cmd


class RedisMiddleware(BaseMiddleware):
    __redis: Redis = None

    def __filters(self, event: MessageMin):
        return get_event_payload_cmd(event) == GetPasswordCommand.key

    async def pre(self) -> None:
        if not self.__filters(self.event):
            return
        if self.__redis is None:
            logger.info('creating redis pool')
            self.__redis = await get_redis()
        self.send({'redis': self.__redis})
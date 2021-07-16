import datetime
import json
from typing import List

from pydantic import BaseModel
from vkbottle import API, Bot
from vkbottle.tools.test_utils import MockedClient

from src.settings import GROUP_ID, TECHNICAL_ADMIN_ID


class Message(BaseModel):
    text: str
    from_id: int = TECHNICAL_ADMIN_ID
    on_datetime: datetime.datetime


def build_raw_vk_message_event(message: Message) -> dict:
    """Сгенерить одно сообщение ВК."""
    return {
        "type": "message_new",
        "object": {
            "message": {
                "date": int(message.on_datetime.timestamp()),
                "from_id": message.from_id,
                "id": 1771,
                "out": 0,
                "peer_id": message.from_id,
                "text": message.text,
                "conversation_message_id": 1302,
                "fwd_messages": [],
                "important": False,
                "random_id": 0,
                "attachments": [],
                "is_hidden": False,
            },
            "client_info": {
                "button_actions": [
                    "text",
                    "intent_subscribe",
                    "intent_unsubscribe",
                ],
                "keyboard": True,
                "inline_keyboard": False,
                "carousel": False,
                "lang_id": 3,
            },
        },
        "group_id": GROUP_ID,
        "event_id": "15cd5841e6fa2ba10c4b4d114a8dc04f78fc47b4",
    }


def build_updates(list_messages: List[Message]):
    """Сгенерить апдейт из кучи сообщений."""
    return {
        "ts": 1,
        "updates": [build_raw_vk_message_event(message) for message in list_messages],
    }


def build_fake_api(list_messages: List[Message]) -> API:
    # Все подобрано как отвечает реальный ВК, поэтому дважды подумайте, прежде чем менять
    # Забрал с https://github.com/timoniq/vkbottle/blob/c6ebefb/tests/bot_test.py
    def callback(data: dict):
        # Этот парень нужен
        if "groups.getById" in data["url"]:
            return {"response": [{"id": 1}]}
        # И этот тоже
        elif "groups.getLongPollServer" in data["url"]:
            return {"response": {"ts": 1, "server": "!SERVER!", "key": ""}}
        # И этот тоже
        elif "!SERVER!" in data["url"]:
            return build_updates(list_messages=list_messages)
        # Отправка сообщений со стороны бота.
        elif "messages.send" in data["url"]:
            target_data = data["data"]
            if "keyboard" in target_data:
                try:
                    json.dumps(target_data["keyboard"])
                except TypeError:
                    target_data["keyboard"] = target_data["keyboard"].get_json()
            return json.dumps({"response": {**data["data"], **{"r": 1}}})

    # Создадим API, в котором клиент будет ходить на коллбеки выше ВМЕСТО vk.com
    api = API("token")
    api.http._session = MockedClient(None, callback=callback)
    return api


async def handle_next_message(bot: Bot):
    """Прокрутить боту следующее сообщение, затем отдать управление обратно."""
    async for event in bot.polling.listen():
        # Придут ивенты из fake_vk_api_message_builder
        assert "updates" in event
        for update in event["updates"]:
            await bot.router.route(update, bot.api)
            yield
        # Но в конце бот будет бесконечно ждать новых сообщений
        # Это фиксится одним break
        break

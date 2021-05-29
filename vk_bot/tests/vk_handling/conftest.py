import datetime

import pytest
import json
from pathlib import Path
from vkbottle import API
from vkbottle.tools.test_utils import MockedClient

basedir = Path(__file__).parent


@pytest.fixture(autouse=True)
def prepared_blueprints_paths(monkeypatch):
    monkeypatch.chdir(basedir.parent.parent / 'src')
    monkeypatch.syspath_prepend(basedir.parent.parent / 'src')
    yield


# Взял это из реального сообщения ВК
EXAMPLE_MESSAGE_EVENT = {
    "ts": 1,
    "updates": [
        {
            "type": "message_new",
            "object": {
                "message": {
                    "date": 1620678005,
                    "from_id": 92540660,
                    "id": 1771,
                    "out": 0,
                    "peer_id": 92540660,
                    "text": "hey hey do the zombies stomp?",
                    "conversation_message_id": 1302,
                    "fwd_messages": [

                    ],
                    "important": False,
                    "random_id": 0,
                    "attachments": [

                    ],
                    "is_hidden": False
                },
                "client_info": {
                    "button_actions": [
                        "text",
                        "intent_subscribe",
                        "intent_unsubscribe"
                    ],
                    "keyboard": True,
                    "inline_keyboard": False,
                    "carousel": False,
                    "lang_id": 3
                }
            },
            "group_id": 204187299,
            "event_id": "15cd5841e6fa2ba10c4b4d114a8dc04f78fc47b4"
        },
    ],
}


@pytest.fixture()
def raw_message_builder():
    """
    Собирает сообщение по шаблону при заданных параметрах.
    При изменениях API вк надо будет изменить шаблон :(

    :return:
    """
    def build_message(
            text: str,
            from_id: int = 92540660,
            on_datetime: datetime.datetime = datetime.datetime.fromtimestamp(1620678005),
            n_messages: int = 1
    ):
        rv = EXAMPLE_MESSAGE_EVENT
        rv['updates'][0]['object']['message']['date'] = on_datetime.timestamp()
        rv['updates'][0]['object']['message']['from_id'] = from_id
        rv['updates'][0]['object']['message']['peer_id'] = from_id
        rv['updates'][0]['object']['message']['text'] = text
        for i in range(n_messages - 1):
            rv['updates'].append(rv['updates'][-1].copy())
        return rv
    return build_message


@pytest.fixture()
def fake_vk_api_message_builder(
        raw_message_builder
):
    def api_builder(
        text: str,
        from_id: int = 92540660,
        on_datetime: datetime.datetime = datetime.datetime.fromtimestamp(1620678005),
        n_messages: int = 1
    ):
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
                return raw_message_builder(text=text, from_id=from_id, on_datetime=on_datetime, n_messages=n_messages)
            # Отправка сообщений со стороны бота.
            elif "messages.send" in data["url"]:
                target_data = data['data']
                if 'keyboard' in target_data:
                    try:
                        json.dumps(target_data['keyboard'])
                    except TypeError:
                        target_data['keyboard'] = target_data['keyboard'].get_json()
                return json.dumps({"response": {**data['data'], **{"r": 1}}})

        # Создадим API, в котором клиент будет ходить на коллбеки выше ВМЕСТО vk.com
        api = API("token")
        api.http._session = MockedClient(None, callback=callback)
        return api
    return api_builder

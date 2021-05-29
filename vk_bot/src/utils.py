import json
from vkbottle.tools.dev_tools.mini_types.bot.message import MessageMin
from typing import Union


def get_event_payload_cmd(event: MessageMin) -> Union[str, None]:
    try:
        payload = json.loads(event.payload)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload.get('cmd')

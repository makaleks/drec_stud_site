from typing import Dict, Optional

from vkbottle import ABCStateDispenser
from vkbottle_types import BaseStateGroup, StatePeer


class ReportingStates(BaseStateGroup):
    DEFAULT = 0
    IS_WRITING = 1


class DatabaseState(ABCStateDispenser):
    def __init__(self):
        super().__init__()
        self.dictionary: Dict[int, StatePeer] = {}

    async def get(self, peer_id: int) -> Optional[StatePeer]:
        return self.dictionary.get(
            peer_id,
            # По умолчанию DEFAULT
            StatePeer(peer_id=peer_id, state=ReportingStates.DEFAULT, payload={}),
        )

    async def set(self, peer_id: int, state: BaseStateGroup, **payload):
        self.dictionary[peer_id] = StatePeer(
            peer_id=peer_id, state=state, payload=payload
        )

    async def delete(self, peer_id: int):
        self.dictionary.pop(peer_id)

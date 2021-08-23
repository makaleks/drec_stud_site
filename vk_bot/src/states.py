from typing import Dict, Optional

from vkbottle import ABCStateDispenser
from vkbottle_types import BaseStateGroup, StatePeer


class ReportingStates(BaseStateGroup):
    DEFAULT = 0
    IS_WRITING = 1


class RegistrationStates(BaseStateGroup):
    # required_keys = {'first_name', 'last_name', 'group_number', 'room_number', 'account_id'}
    DEFAULT = 0
    WRITING_GROUP_NUMBER = 10
    WRITING_ROOM_NUMBER = 11
    APPROVING_INPUT = 12


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
        new_payload = (await self.get(peer_id)).payload
        new_payload.update(payload)
        self.dictionary[peer_id] = StatePeer(
            peer_id=peer_id, state=state, payload=new_payload
        )

    async def delete(self, peer_id: int):
        self.dictionary.pop(peer_id)

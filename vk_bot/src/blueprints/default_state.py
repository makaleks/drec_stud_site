from loguru import logger
from vkbottle import BotBlueprint
from vkbottle.bot import Message, rules

from src.states import ReportingStates

bl = BotBlueprint(name="default_state")
bl.labeler.auto_rules = [rules.PeerRule(from_chat=False)]


@bl.labeler.message(blocking=False)
async def set_default_state(message: Message):
    user, state = message.from_id, ReportingStates.DEFAULT
    if await bl.state_dispenser.get(user) is None:
        logger.debug(f"setting state {state} for user={user}")
        await bl.state_dispenser.set(user, state)

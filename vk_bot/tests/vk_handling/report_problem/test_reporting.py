from typing import List

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from src.blueprints.defaults import hello_admin
from src.blueprints.reporting import cancel
from src.states import ReportingStates
from tests.utils import Message, build_fake_api, handle_next_message


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="cancel")
@parametrize(
    "state, should_call",
    [
        (None, hello_admin),
        (ReportingStates.IS_WRITING, cancel),
    ],
)
async def test_correct_state_calls_correct_handlers_on_cancellation_command(
    messages: List[Message], state, should_call, build_fake_bot, mock_bot_handlers
):
    # GIVEN: bot in state
    bot = build_fake_bot(fake_api=build_fake_api(messages))
    if state:
        bot.state_dispenser.set(messages[0].from_id, state)
    bot, target_mock, other_mocks = mock_bot_handlers(
        bot=bot, expected_handler=should_call
    )
    # WHEN: bot receives cancellation command from user
    async for _ in handle_next_message(bot):
        pass
    # THEN: target handler is called
    target_mock.assert_called_once()
    # THEN: no others are called
    for h in other_mocks:
        h.assert_not_called()

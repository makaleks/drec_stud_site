import datetime

import pytest
from pytest_cases import parametrize_with_cases

from tests.utils import Message, build_fake_api, handle_next_message


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(
    argnames="text, from_id, expected_handler", cases=".cases_vk_messages"
)
async def test_correct_handler_based_on_text(
    build_fake_bot, mock_bot_handlers, text, from_id, expected_handler
):
    # GIVEN: prepared bot
    bot = build_fake_bot(
        fake_api=build_fake_api(
            [
                Message(
                    text=text,
                    from_id=from_id,
                    on_datetime=datetime.datetime(2021, 7, 13),
                )
            ]
        ),
    )
    bot, target_mock, other_mocks = mock_bot_handlers(
        bot=bot,
        expected_handler=expected_handler,
    )
    # WHEN: bot reads all messages from current test case
    async for _ in handle_next_message(bot):
        pass
    # THEN: bot calls handler once
    target_mock.assert_called_once()
    # THEN: no other handler is called
    for mock in other_mocks:
        mock.assert_not_called()

import datetime
from typing import Callable

import pytest
from pytest_cases import fixture, parametrize_with_cases, unpack_fixture
from pytest_mock import MockFixture
from vkbottle import Bot

from tests.utils import Message, build_fake_api


@fixture
def mock_bot_handlers(mocker: MockFixture):
    """Мокнуть все хендлеры -- expected_handler отдельно."""

    def bot_builder(bot: Bot, expected_handler: Callable):
        target_mock = None
        other_mocks = []
        for handler in bot.labeler.message_view.handlers:
            tmp_mock = mocker.AsyncMock()
            handler.handle = tmp_mock
            if expected_handler.__name__ == handler.handler.__name__:
                # Целевой мок отдельно
                target_mock = tmp_mock
            else:
                # Остальные списком - отдельно
                other_mocks.append(tmp_mock)
        return bot, target_mock, other_mocks

    return bot_builder


@fixture
@parametrize_with_cases(
    argnames="text, from_id, expected_handler", cases=".cases_vk_messages"
)
def bot_with_mocks(build_fake_bot, mock_bot_handlers, text, from_id, expected_handler):
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
    return mock_bot_handlers(
        bot=bot,
        expected_handler=expected_handler,
    )


unpack_fixture("bot, target_mock, other_mocks", "bot_with_mocks")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_correct_handler_based_on_text(bot, target_mock, other_mocks):
    # GIVEN: prepared bot
    # WHEN: bot receives a message with unknown command
    async for event in bot.polling.listen():
        # Придут ивенты из fake_vk_api_message_builder
        assert "updates" in event
        for update in event["updates"]:
            await bot.router.route(update, bot.api)
        # Но в конце бот будет бесконечно ждать новых сообщений
        # Это фиксится одним break
        break
    # THEN: bot calls handler once
    target_mock.assert_called_once()
    # THEN: no other handler is called
    for mock in other_mocks:
        mock.assert_not_called()

import pytest
from pytest_mock import MockFixture
from typing import Callable
from pytest_cases import parametrize_with_cases, fixture, unpack_fixture


@fixture
@parametrize_with_cases('text, from_id, expected_handler')
def fake_bot_builder(
        text: str,
        from_id: int,
        expected_handler: Callable,
        fake_vk_api_message_builder,
        monkeypatch,
        mocker: MockFixture
):
    monkeypatch.setenv('SECRET_BOT_TOKEN', '')
    from src.bot import bot
    bot.api = fake_vk_api_message_builder(
        from_id=from_id,
        text=text
    )
    target_mock = None
    other_mocks = []
    for handler in bot.labeler.message_view.handlers:
        tmp_mock = mocker.AsyncMock()
        handler.handle = tmp_mock
        if expected_handler.__name__ == handler.handler.__name__:
            target_mock = tmp_mock
        else:
            other_mocks.append(tmp_mock)
    return bot, target_mock, other_mocks


bot, target_mock, other_mocks = unpack_fixture('bot, target_mock, other_mocks', fake_bot_builder)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_correct_handler_based_on_text(bot, target_mock, other_mocks):
    # GIVEN: prepared bot
    # WHEN: bot receives a message with unknown command
    async for event in bot.polling.listen():
        # Придут ивенты из fake_vk_api_message_builder
        assert 'updates' in event
        for update in event['updates']:
            await bot.router.route(update, bot.api)
        # Но в конце бот будет бесконечно ждать новых сообщений
        # Это фиксится одним break
        break
    # THEN: bot calls handler once
    target_mock.assert_called_once()
    # THEN: no other handler is called
    for mock in other_mocks:
        mock.assert_not_called()

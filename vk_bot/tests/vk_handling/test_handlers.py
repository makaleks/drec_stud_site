import pytest
from pytest_mock import MockFixture
from pytest_cases import parametrize_with_cases


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases("text, from_id, expected_handler")
async def test_correct_handler_based_on_text(
        text,
        from_id,
        expected_handler,
        fake_vk_api_message_builder,
        mocker: MockFixture,
):
    # GIVEN: prepared bot
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

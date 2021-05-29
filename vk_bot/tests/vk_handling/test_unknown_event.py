import pytest
from pytest_mock import MockFixture


@pytest.mark.asyncio
@pytest.mark.parametrize('text', [
    'command fialw', 'фывйцв', 'smtgsh'
])
@pytest.mark.unit
async def test_goes_to_fallback_on_unknown_message(
        text,
        mocker: MockFixture,
        fake_vk_api_message_builder
):
    # GIVEN: prepared bot
    from src.bot import bot
    # WHEN: bot receives a message with unknown command
    bot.api = fake_vk_api_message_builder(text=text)
    mock = mocker.AsyncMock()

    # THEN: bot calls fallback handler
    for handler in bot.labeler.message_view.handlers:
        if 'hello_admin' in str(handler):
            handler.handle = mock

    async for event in bot.polling.listen():
        # Придут ивенты из fake_vk_api_message_builder
        assert 'updates' in event
        for update in event['updates']:
            await bot.router.route(update, bot.api)
        # Но в конце бот будет бесконечно ждать новых сообщений
        # Это фиксится одним break
        break
    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_default_fallback_is_last_in_handlers_list():
    # GIVEN: prepared environment
    # WHEN: bot is build
    from src.bot import bot
    # THEN: default handler goes to the last of handlers' list
    all_handlers = bot.labeler.message_view.handlers
    position = None
    for i, handler in enumerate(all_handlers):
        if 'hello_admin' in str(handler):
            position = i
    assert position == len(all_handlers) - 1

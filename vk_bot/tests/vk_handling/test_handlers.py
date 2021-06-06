import pytest
from pytest_cases import unpack_fixture, parametrize_with_cases, fixture


@fixture
@parametrize_with_cases(argnames='text, from_id, expected_handler', cases='.cases_vk_messages')
def build_bot(fake_bot_builder, text, from_id, expected_handler):
    return fake_bot_builder(text=text, from_id=from_id, expected_handler=expected_handler)


bot, target_mock, other_mocks = unpack_fixture('bot, target_mock, other_mocks', 'build_bot')


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

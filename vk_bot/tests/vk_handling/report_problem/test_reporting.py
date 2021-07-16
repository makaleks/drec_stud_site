from typing import List

import pytest
from pytest_cases import parametrize, parametrize_with_cases
from pytest_mock import MockFixture

import src.blueprints.reporting as rep
from src.blueprints.defaults import hello_admin
from src.states import ReportingStates
from tests.utils import Message, build_fake_api, handle_next_message


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="cancel")
@parametrize(
    "state, should_call",
    [
        (ReportingStates.DEFAULT, hello_admin),
        (ReportingStates.IS_WRITING, rep.report_problem_finish),
    ],
)
async def test_correct_state_calls_correct_handlers_on_cancellation_command(
    messages: List[Message], state, should_call, build_fake_bot, mock_bot_handlers
):
    # GIVEN: бот и юзер в нужном состоянии
    bot = build_fake_bot(fake_api=build_fake_api(messages))
    await bot.state_dispenser.set(messages[0].from_id, state)
    bot, target_mock, other_mocks = mock_bot_handlers(
        bot=bot, expected_handler=should_call
    )
    # WHEN: бот получает команду "отмена" от юзера
    async for _ in handle_next_message(bot):
        pass
    # THEN: вызывается нужный хендлер
    target_mock.assert_called_once()
    # THEN: другие хендлеры не вызываются
    for h in other_mocks:
        h.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="start_report")
async def test_start_report_changes_state(messages: List[Message], build_fake_bot):
    # GIVEN: bot and user without state
    bot = build_fake_bot(fake_api=build_fake_api(messages))
    # WHEN: bot handles "start_report" message
    async for _ in handle_next_message(bot):
        pass
    # THEN: user state is changed
    assert (
        await bot.state_dispenser.get(messages[0].from_id)
    ).state == ReportingStates.IS_WRITING


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="dummy_report")
async def test_submitted_report_calls_correct_handler(
    messages: List[Message], build_fake_bot, mock_bot_handlers, mocker: MockFixture
):
    # GIVEN: bot and user in WRITING state
    bot = build_fake_bot(fake_api=build_fake_api(messages))
    bot, target_mock, others = mock_bot_handlers(
        bot=bot, expected_handler=rep.report_problem_finish
    )
    await bot.state_dispenser.set(messages[0].from_id, ReportingStates.IS_WRITING)
    # WHEN: bot handles arbitrary text as a message
    async for _ in handle_next_message(bot):
        pass
    # THEN: correct handler is called
    target_mock.assert_called_once()
    # THEN: no other handlers are called
    for h in others:
        h.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="dummy_report")
async def test_submitted_report_writes_message_to_admin(mocker: MockFixture, messages):
    # GIVEN: message with report
    mock1 = mocker.AsyncMock()
    mock1.text = messages[0].text
    mocker.patch("src.blueprints.reporting.bl", mock1)

    mock = mocker.AsyncMock()
    mocker.patch("src.blueprints.reporting.report_to_admin", mock)
    # WHEN: `report_problem` handler is called
    await rep.report_problem_finish(mock1)
    # THEN: `send_message_to_admin` is called awaited
    mock.assert_awaited()


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(argnames="messages", glob="dummy_report")
async def test_submitted_report_changes_state_to_default(mocker: MockFixture, messages):
    # GIVEN: message with report
    mock1 = mocker.AsyncMock()
    mock1.text = messages[0].text
    mocker.patch("src.blueprints.reporting.bl", mock1)

    mock = mocker.AsyncMock()
    mocker.patch("src.blueprints.reporting.report_to_admin", mock)
    # WHEN: `report_problem` handler is called
    await rep.report_problem_finish(mock1)
    # THEN: `set` in state_dispenser is called awaited
    mock1.state_dispenser.set.assert_awaited()

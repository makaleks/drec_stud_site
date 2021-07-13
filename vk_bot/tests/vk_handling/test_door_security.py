import pytest
from pytest_cases import parametrize, parametrize_with_cases
from pytest_mock import MockFixture

from src.settings import ADMIN_HARDCODED_LIST
from src.utils import process_door_command


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(cases=".cases_service_id", argnames="service_id")
@parametrize_with_cases(
    cases=".cases_server_open_response", glob="*", argnames="mocked_server"
)
@parametrize(
    **{
        "user_id": ADMIN_HARDCODED_LIST,
    }
)
async def test_admin_can_open_anytime(
    mocker: MockFixture,
    service_id: str,
    user_id: int,
    # GIVEN: server what always give `no_orders` message
    mocked_server,
):
    # WHEN: admin wants to open the door
    lockbox_mock = mocker.AsyncMock()
    mocker.patch("src.utils.send_signal_door_open", lockbox_mock)
    message_mock = mocker.AsyncMock()
    message_mock.from_id = user_id
    await process_door_command(message_mock, service_id, "hello there", do_open=True)
    # THEN: the door opens
    lockbox_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(cases=".cases_service_id", argnames="service_id")
@parametrize_with_cases(
    cases=".cases_server_open_response", glob="*yes", argnames="mocked_server"
)
@parametrize(**{"user_id": [188477847]})
async def test_usual_user_can_open_during_order(
    mocker: MockFixture,
    user_id: int,
    service_id: str,
    # GIVEN: server what always give `yes` message
    mocked_server,
):
    # WHEN: regular user wants to open the door
    lockbox_mock = mocker.AsyncMock()
    mocker.patch("src.utils.send_signal_door_open", lockbox_mock)
    message_mock = mocker.AsyncMock()
    message_mock.from_id = user_id
    await process_door_command(message_mock, service_id, "hello there", do_open=True)
    # THEN: the door opens
    lockbox_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
@parametrize_with_cases(cases=".cases_service_id", argnames="service_id")
@parametrize_with_cases(
    cases=".cases_server_open_response", glob="*no", argnames="mocked_server"
)
@parametrize(**{"user_id": [188477847]})
async def test_usual_user_cannot_open_without_order(
    mocker: MockFixture,
    user_id: int,
    service_id: str,
    # GIVEN: server what always give `no_orders` message
    mocked_server,
):
    # WHEN: regular user wants to open the door
    lockbox_mock = mocker.AsyncMock()
    mocker.patch("src.utils.send_signal_door_open", lockbox_mock)
    message_mock = mocker.AsyncMock()
    message_mock.from_id = user_id
    await process_door_command(message_mock, service_id, "hello there", do_open=True)
    # THEN: the door does not opens
    lockbox_mock.assert_not_called()

import os

import pytest
import aioredis
from unittest.mock import AsyncMock
from pytest_mock import MockFixture
from typing import Tuple, List

from src.redis_.crud import set_password_for_user, get_password_from_redis, get_redis


@pytest.mark.good_input
@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_password_from_filled_redis_gives_correct_data(
        fake_credentials: List[Tuple[int, str]], redis_filled: aioredis.Redis):
    # GIVEN: filled redis database
    # WHEN: calling get_password_from_redis
    # THEN: correct data is obtained
    for user_id, expected_password in fake_credentials:
        assert expected_password == await get_password_from_redis(redis_filled, user_id)


@pytest.mark.good_input
@pytest.mark.unit
@pytest.mark.asyncio
async def test_set_password_does_not_fail(
        fake_credentials, redis_empty
):
    # GIVEN: empty redis database
    # WHEN: calling set_password_for_user
    # THEN: nothing fails
    for user_id, password in fake_credentials:
        await set_password_for_user(redis_empty, user_id, password)


@pytest.mark.good_input
@pytest.mark.functional
@pytest.mark.asyncio
async def test_set_and_get_password_give_same_results(
        redis_empty, fake_credentials
):
    # GIVEN: empty redis database
    # WHEN: calling set_password_for_user
    for user_id, password in fake_credentials:
        await set_password_for_user(redis_empty, user_id, password)
    # THEN: get_password_for_user will give correct results
    for user_id, expected_password in fake_credentials:
        assert expected_password == await get_password_from_redis(redis_empty, user_id)


@pytest.mark.good_input
@pytest.mark.integrational
@pytest.mark.asyncio
async def test_get_redis_uses_os_variable(mocker: MockFixture):
    # GIVEN: Redis database URL
    FAKE_URL = "redis://admin:admin@hosthost.com:9870/"
    ENV_KEY = "REDISTOGO_URL"
    mocker.patch.dict(os.environ, {ENV_KEY: FAKE_URL})
    mock = mocker.AsyncMock()
    mocker.patch.object(aioredis, 'create_redis_pool', mock)
    # WHEN: get_redis() is called
    await get_redis()
    # THEN: it reads from os.environ.get('REDISTOGO_URL')
    mock.assert_called_with(FAKE_URL)


@pytest.mark.good_input
@pytest.mark.unit
@pytest.mark.asyncio
async def test_closes_connection_after_transaction(redis_empty, close_redis_mock: AsyncMock):
    # GIVEN: empty redis database
    # WHEN: calling any redis method
    # THEN: connection being properly closed
    await set_password_for_user(redis_empty, 1, '1')
    assert close_redis_mock.call_count == 1
    await get_password_from_redis(redis_empty, 1)
    assert close_redis_mock.call_count == 2


@pytest.fixture()
async def fake_credentials(redis_empty: aioredis.Redis):
    creds = [(i, str(i) * 10) for i in range(10)]
    yield creds

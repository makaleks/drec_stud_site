import aioredis
import fakeredis.aioredis
import pytest
from pytest_mock import MockFixture


@pytest.fixture()
async def redis_empty(close_redis_mock):
    redis = await fakeredis.aioredis.create_redis_pool()
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture()
async def close_redis_mock(mocker: MockFixture):
    quit_mock = mocker.AsyncMock()
    # fakeredis does not support 'QUIT', so need to mock it
    mocker.patch.object(aioredis.Redis, 'quit', quit_mock)
    return quit_mock


@pytest.fixture()
async def redis_filled(redis_empty, fake_credentials):
    for u, p in fake_credentials:
        await redis_empty.set(u, p)
    return redis_empty
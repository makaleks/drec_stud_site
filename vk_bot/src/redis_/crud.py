import aioredis
import os


async def get_redis() -> aioredis.Redis:
    return await aioredis.create_redis_pool(os.environ.get('REDISTOGO_URL'))


async def get_password_from_redis(redis: aioredis.Redis, user_id: int) -> str:
    rv = await redis.get(user_id)
    await redis.quit()
    return (rv or b'').decode('utf-8')


async def set_password_for_user(redis: aioredis.Redis, user_id: int, password: str) -> bool:
    rv = await redis.set(user_id, password)
    await redis.quit()
    return rv

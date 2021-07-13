import asyncio
import datetime
import sys
from pathlib import Path

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from loguru import logger

basedir = Path(__file__).parent


async def check_lock(ip: str, display_name: str, port: str = 8085):
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"http://{ip}:{port}/health_check", timeout=3
                ) as r:
                    if r.status != 200:
                        logger.critical(f"lockbox is down: {display_name} [{ip}]")
            except Exception as e:
                logger.critical(f"lockbox is down: {display_name} [{ip}]")
            finally:
                await asyncio.sleep(3)


if __name__ == "__main__":
    # Set up logger
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    logger.add(
        basedir / "logs" / "log_{time}.log",
        rotation=datetime.timedelta(days=1),
        retention=30,
        level="INFO",
    )

    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            *[
                check_lock(ip=ip, display_name=display_name)
                for ip, display_name in (("10.55.99.5", "5b"), ("10.55.99.6", "6b"))
            ]
        )
    )

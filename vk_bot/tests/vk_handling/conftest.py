import datetime
from pathlib import Path
from typing import Callable

import pytest
from pytest_cases import fixture
from pytest_mock import MockFixture

from tests.utils import Message, build_fake_api

basedir = Path(__file__).parent


@pytest.fixture(autouse=True)
def prepared_blueprints_paths(monkeypatch):
    monkeypatch.chdir(basedir.parent.parent / "src")
    monkeypatch.syspath_prepend(basedir.parent.parent / "src")
    yield


@fixture
def fake_bot_builder(monkeypatch, mocker: MockFixture):
    def bot_builder(text: str, from_id: int, expected_handler: Callable):
        monkeypatch.setenv("SECRET_BOT_TOKEN", "")
        from src.bot import bot

        bot.api = build_fake_api(
            [
                Message(
                    from_id=from_id,
                    text=text,
                    on_datetime=datetime.datetime(2021, 7, 13),
                )
            ]
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

    return bot_builder

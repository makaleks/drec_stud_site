from pathlib import Path
from typing import Callable

import pytest
from pytest_cases import fixture
from pytest_mock import MockFixture
from vkbottle import API, Bot

basedir = Path(__file__).parent


@pytest.fixture(autouse=True)
def prepared_blueprints_paths(monkeypatch):
    monkeypatch.chdir(basedir.parent.parent / "src")
    monkeypatch.syspath_prepend(basedir.parent.parent / "src")
    yield


@fixture
def build_fake_bot(monkeypatch):
    def bot_builder(fake_api: API):
        monkeypatch.setenv("SECRET_BOT_TOKEN", "")
        from src.bot import bot

        bot.api = fake_api
        return bot

    return bot_builder


@fixture
def mock_bot_handlers(mocker: MockFixture):
    """Мокнуть все хендлеры -- expected_handler отдельно."""

    def bot_builder(bot: Bot, expected_handler: Callable):
        target_mock = None
        other_mocks = []
        for handler in bot.labeler.message_view.handlers:
            tmp_mock = mocker.AsyncMock()
            handler.handle = tmp_mock
            if expected_handler.__name__ == handler.handler.__name__:
                # Целевой мок отдельно
                target_mock = tmp_mock
            else:
                # Остальные списком - отдельно
                other_mocks.append(tmp_mock)
        return bot, target_mock, other_mocks

    return bot_builder

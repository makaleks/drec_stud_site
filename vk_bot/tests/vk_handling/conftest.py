from pathlib import Path

import pytest
from pytest_cases import fixture
from vkbottle import API

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

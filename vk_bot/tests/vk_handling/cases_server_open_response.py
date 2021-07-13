"""Set up server response whether user is allowed to open or not."""
import json

from pytest_mock import MockFixture


class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


def case_yes(mocker: MockFixture):
    data = {"status": "yes"}
    mocker.patch(
        "aiohttp.ClientSession.get", return_value=MockResponse(json.dumps(data), 200)
    )
    return


def case_no(mocker: MockFixture):
    data = {"status": "no"}
    mocker.patch(
        "aiohttp.ClientSession.get", return_value=MockResponse(json.dumps(data), 200)
    )
    return

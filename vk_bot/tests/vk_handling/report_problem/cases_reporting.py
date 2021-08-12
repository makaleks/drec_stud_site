import datetime

from pytest_cases import parametrize

from src.commands import CancelAction, ReportProblemStart
from tests.utils import Message


def case_start_report():
    uid = 188477847
    dt = datetime.datetime(2021, 7, 13)
    return [
        Message(
            from_id=uid,
            text=f"{ReportProblemStart.button_name}",
            on_datetime=dt,
        ),
    ]


def case_cancel():
    uid = 188477847
    dt = datetime.datetime(2021, 7, 13)
    return [
        Message(
            from_id=uid,
            text=f"{CancelAction.button_name}",
            on_datetime=dt,
        ),
    ]


@parametrize(
    "message",
    [
        "В стиралке 5Б не работает генератор мемов",
        "В моей машине отмывают деньги",
        "Кроссовки от физры стерли мои посещения",
    ],
)
def case_dummy_report(message):
    uid = 188477847
    dt = datetime.datetime(2021, 7, 13)
    return [
        Message(
            from_id=uid,
            text=message,
            on_datetime=dt,
        ),
    ]

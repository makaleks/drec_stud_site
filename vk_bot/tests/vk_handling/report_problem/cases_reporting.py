import datetime

from pytest_cases import parametrize

from src.commands import CancelAction, ReportProblemStart
from tests.utils import Message


@parametrize(**{"prefix": ["!", "/"]})
def case_non_admin_starts_report_and_quits(prefix):
    uid = 188477847
    dt = datetime.datetime(2021, 7, 13)
    return [
        Message(
            from_id=uid,
            text=f"{prefix}{ReportProblemStart.raw_message_name}",
            on_datetime=dt,
        ),
        Message(
            from_id=uid, text=f"{prefix}{CancelAction.raw_message_name}", on_datetime=dt
        ),
    ]


@parametrize(**{"prefix": ["!", "/"]})
def case_cancel(prefix):
    uid = 188477847
    dt = datetime.datetime(2021, 7, 13)
    return [
        Message(
            from_id=uid,
            text=f"{prefix}{CancelAction.raw_message_name}",
            on_datetime=dt,
        ),
    ]

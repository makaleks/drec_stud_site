import datetime


def extract_from_minutes(value):
    '''
    Extracts all datetime/time data longer than minute (including).
    In case the ``time`` provided, the ``date`` in return will be ``date.min``.

    :param value: datetime or time to extract minuted
    :type value: datetime, time
    :rtype: datetime

    .. warning:: In case the ``time`` provided, the ``date`` in return will be ``date.min``.
    '''
    if isinstance(value, datetime.time):
        t = datetime.time(hour = value.hour, minute = value.minute)
        return datetime.datetime.combine(datetime.date.min, t)
    elif isinstance(value, datetime.datetime):
        t = datetime.time(hour = value.time().hour, minute = value.time().minute)
        return datetime.datetime.combine(value.date(), t)
    else:
        raise TypeError('value({0}) must be datetime or time'.format(value.__class__.__name__))


def adjust_start_end(start, end):
    '''
    Returns [start, end] as datetimes.
    Throws exceptions on type errors and if datetime ``start`` < ``end``.
    In case just the ``time`` provided and ``start`` > ``end``, the ``end`` will have ``+1`` day.

    :param start: order start
    :param end: order end
    :type start: datetime, time (same as ``end``)
    :type end: datetime, time (same as ``start``)
    :returns [start, end]
    :rtype: list (of datetime)

    .. warning:: In case just the ``time`` provided and ``start`` > ``end``, the ``end`` will have ``+1`` day.
    '''
    delta = datetime.timedelta()
    if all(isinstance(dt, datetime.time) for dt in [start, end]):
        if start >= end:
            delta = datetime.timedelta(days = 1)
    elif all(isinstance(dt, datetime.datetime) for dt in [start, end]):
        if start > end:
            raise ValueError('need start({0}) > end({1})'.format(start, end))
    else:
        raise TypeError('start({0}) and end({1}) must be both datetime or time')
    start = extract_from_minutes(start)
    end = extract_from_minutes(end) + delta
    return [start, end]


import datetime
from .util import adjust_start_end

class TimetableInterval:
    '''
    This class of Timetable interval.
    The used model is '[start, end)'
    The objects of this class should not be generated manually, so all fields are read-only.

    :var start: readonly, interval start, always >= ``end``
    :var end: readonly, interval end, always <= ``start``
    :var is_open: readonly, if the interval can be ordered
    :var timesteps_num: readonly, number of timesteps, used in interval
    :var orders: readonly, orders, linked to this timetable interval
    :var is_now: readonly, if the interval contains 'now', provided at __init__ (the used model is '[start, end)')
    :type start: datetime
    :type end: datetime
    :type is_open: bool
    :type timesteps_num: int (positive)
    :type orders: list (of ``TimetableOrder``)
    :type is_now: bool
    '''
    def __init__(self, start, end, is_open = True, timesteps_num = 1, orders = [], now = None):
        '''
        Initializes the ``TimetableInterval``.
        In case just the ``time`` provided and ``start`` > ``end``, the ``end`` will have ``+1`` day.

        :param start: interval start
        :param end: interval end
        :param is_open: if the interval can be ordered
        :param timesteps_num: number of timesteps, used in interval
        :param orders: orders, linked to this timetable interval
        :param now: optional (default=``None``), the reference for the ``is_now`` field (the used model is '[start, end)')
        :type start: datetime, time (same as ``end``)
        :type end: datetime, time (same as ``start``)
        :type is_open: bool
        :type timesteps_num: int (positive)
        :type orders: list (of ``TimetableOrder``)
        :type now: datetime, None
        '''
        if not isinstance(timesteps_num, int) or timesteps_num <= 0:
            raise TypeError('timesteps_num({0}) must be int > 0'.format(timesteps_num.__class__.__name__))
        elif now is not None and not isinstance(now, datetime.datetime):
            raise TypeError('now({0}) must be datetime or None'.format(now.__class__.__name__))
        start_end = adjust_start_end(start, end)
        self._start = start_end[0]
        self._end = start_end[1]
        self._is_open = is_open
        self._timesteps_num = timesteps_num
        self.orders = orders
        if now is not None:
            self._is_now = (self._start <= now and now < self._end)
        else:
            self._is_now = False
    def __str__(self):
        return '({0}-{1} {2}{3})'.format(self.start.strftime('%H:%M'), self.end.strftime('%H:%M'), 'opened' if self.is_open else 'closed', ' orders={0}'.format(str(self.orders)) if self.orders else '')
    def __repr__(self):
        return str(self)
    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end
    def get_is_open(self):
        return self._is_open
    def set_is_open(self, is_open):
        if not isinstance(is_open, bool):
            raise TypeError('isopen({0}) must be bool'.format(is_open.__class__.__name__))
        self._is_open = is_open
        return self._is_open
    is_open = property(get_is_open, set_is_open)
    @property
    def timesteps_num(self):
        return self._timesteps_num
    def get_orders(self):
        return self._orders
    def set_orders(self, orders):
        if not isinstance(orders, list) and not all(isinstance(o, OrderedInterval) for o in orders):
            raise TypeError('orders({0}) must be type a list of OrderedInterval'.format(orders.__class__.name__))
        self._orders = orders
        return self._orders
    orders = property(get_orders, set_orders)
    @property
    def is_now(self):
        return self._is_now


import datetime
from types import SimpleNamespace as EmptyObject
from .interval import TimetableInterval
from .util import adjust_start_end


class TimetableIntervalCursor:
    '''
    This class is an iterator (to be used in ``for .. in ..``).
    Produces TimetableInterval, placed between ``start`` and ``stop``.
    The intervals can be produced reversely (go from ``stop`` until ``start`` is reached) to leave free space at the begin, not at the stop of [start, stop).
    The used model is '[start, stop)'
    The objects of this class should not be modified.

    :var start: readonly, where to start the generation, always >= ``stop``
    :var timestep: readonly, the step of interval (the final interval length is ``timestep * timesteps_num``)
    :var stop: readonly, where to stop the generation, always <= ``start``
    :var timesteps_num: readonly, the number of steps to be used in interval (the final interval length is ``timestep * timesteps_num``)
    :var use_reverse: if intervals should be generated in order 'stop->start', not 'start->stop' (default)
    :var now: the reference for the ``is_now`` field of interval
    :type start: datetime
    :type timestep: timedelta
    :type stop: datetime
    :type timesteps_num: int (positive)
    :type use_reverse: bool
    :type now: datetime, None
    '''
    def __init__(self, start, timestep, stop, timesteps_num = 1, use_reverse = False, now = None):
        '''
        Initializes the ``TimetableIntervalCursor``.

        :param start: where to start the generation, always >= ``stop``
        :param stop: where to stop the generation, always <= ``start``
        :param timestep: the step of interval (the final interval length is ``timestep * timesteps_num``)
        :param timesteps_num: the number of steps to be used in interval (the final interval length is ``timestep * timesteps_num``)
        :param use_reverse: optional (default=``False``), if intervals should be generated in order 'stop->start', not 'start->stop' (default)
        :param now: optional (default=``None``), the reference for the ``is_now`` field of interval
        :type start: datetime
        :type stop: datetime
        :type timestep: time, timedelta
        :type timesteps_num: int (positive)
        :type use_reverse: bool
        :type now: datetime, None
        '''
        if isinstance(timestep, datetime.time):
            self._timestep = datetime.datetime.combine(datetime.date.min, timestep) - datetime.datetime.min
        elif isinstance(timestep, datetime.timedelta):
            self._timestep = timestep
        else:
            raise TypeError('timestep({0}) must be time or timedelta'.format(timestep.__class__.__name__))
        if not isinstance(timesteps_num, int) or timesteps_num <= 0:
            raise TypeError('timesteps_num({0}) must be int > 0'.format(timesteps_num.__class__.__name__))
        elif not isinstance(use_reverse, bool):
            raise TypeError('use_reverse({0}) must be bool'.format(use_reverse.__class__.__name__))
        elif now is not None and not isinstance(now, datetime.datetime):
            raise TypeError('now({0}) must be datetime or None'.format(now.__class__.__name__))
        # used to copy {_start, _end} to {_start, _stop} in 'self'
        start_end = adjust_start_end(start, stop)
        self._start = start_end[0]
        self._stop = start_end[1]
        self._timesteps_num = timesteps_num
        self._use_reverse = use_reverse
        self._now = now
        if not use_reverse:
            self._it = start
            self._next = start + timestep*timesteps_num
        else:
            self._it = stop
            self._next = stop - timestep*timesteps_num
    def __iter__(self):
        return self
    def __next__(self):
        if not self.use_reverse:
            if self._next > self._stop:
                raise StopIteration
            else:
                to_ret = TimetableInterval(self._it, self._next, timesteps_num = self._timesteps_num, now = self._now)
                self._it = self._next
                self._next += self._timestep*self._timesteps_num
        else:
            if self._next < self._start:
                raise StopIteration
            else:
                to_ret = TimetableInterval(self._next, self._it, timesteps_num = self._timesteps_num, now = self._now)
                self._it = self._next
                self._next -= self._timestep*self._timesteps_num
        return to_ret
    @property
    def start(self):
        return self._start
    @property
    def stop(self):
        return self._stop
    @property
    def timestep(self):
        return self._timestep
    @property
    def timesteps_num(self):
        return self._timesteps_num
    @property
    def use_reverse(self):
        return self._use_reverse
    @property
    def now(self):
        return self._now


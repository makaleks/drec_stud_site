from .timetable import Timetable

from copy import deepcopy

import datetime


class TimetableList:
    '''
    This class provides group manipulations on Timetables.
    The provided operations are:
        - ``crop_start()`` - set new start position for all timetables with saving the order and the structure of all other cells, useful when 'today' time is passing
        - ``clear_closed_rows()`` - set start/end to leave no full rows of closed timetables` cells
    All input/output elements use ``deepcopy()`` to save the integrity of objects.
    The used model is '[start, end)'

    :var timestep: readonly, the step of intervals, used as same unit, when combining different timetables
    :var global_start: readonly, the common start for all timetables
    :var global_end: readonly, the common end for all timetables
    :type timestep: timedelta
    :type global_start: datetime
    :type global_end: datetime
    '''
    # leave_head_cell - leave 1 'head' cell
    # floor_crop - include 'new_start' cell as 'open'
    def crop_start(self, new_start, leave_head_cell = False, floor_crop = False):
        if not isinstance(new_start, datetime.datetime):
            raise TypeError('new_start({0}) must be datetime'.format(new_start.__class__.__name__))
        elif not isinstance(leave_head_cell, bool):
            raise TypeError('leave_head_cell({0}) must be bool'.format(leave_head_cell.__class__.__name__))
        elif not isinstance(floor_crop, bool):
            raise TypeError('floor_crop({0}) must be bool'.format(floor_crop.__class__.__name__))
        if new_start >= self.global_end:
            for k in self._timetables:
                self._timetables[k].set_start_end(self.global_end, self.global_end)
            return
        elif new_start > self.global_start:
            new_start_was = new_start
            if not floor_crop:
                # --|--found--|+++++++++|++++
                min_end = None
                for t in self._timetables.values():
                    interval = t.find_interval(new_start, add_orders = False)
                    t.set_first_last(interval.end, 
                            t.get_last_start() + t.timestep * t.timesteps_num)
                    if not min_end or interval.end < min_end:
                        min_end = interval.end
                for t in self._timetables.values():
                    t.set_start_end(min_end, self.global_end)
                new_start = min_end
            else:
                # --|++found++|+++++++++|++++
                min_start = None
                for t in self._timetables.values():
                    interval = t.find_interval(new_start, add_orders = False)
                    t.set_first_last(interval.start, 
                            t.get_last_start() + t.timestep * t.timesteps_num)
                    if not min_start or interval.start < min_start:
                        min_start = interval.start
                for t in self._timetables.values():
                    t.set_start_end(min_start, self.global_end)
                new_start = min_start
        else:
            new_start = self.global_start
        if leave_head_cell:
            new_start -= self.timestep
            for t in self._timetables.values():
                t.set_start_end(new_start, self.global_end)
    def clear_closed_rows(self):
        # (for '-'=closed, '+'=opened)
        # ----    -+--
        # ----    ++-+
        # -+-- => ++++
        # ++-+    
        # ++++    
        if not self._timetables:
            return
        # head
        min_len = None
        for t in self._timetables.values():
            l = t.get_head_len()
            if min_len is None or l < min_len:
                min_len = l
        start = self.global_start + self.timestep*min_len
        # tail
        min_len = None
        for t in self._timetables.values():
            l = t.get_tail_len()
            if min_len is None or l < min_len:
                min_len = l
        end = self.global_end - self.timestep*min_len
        for t in self._timetables.values():
            t.set_start_end(start, end)
    def add_timetable(self, dic, force_extend = False):
        if (not isinstance(dic, dict) 
                or (self._timetables and any(k in self._timetables for k in dic))
                or not all(isinstance(t, Timetable) for t in dic.values())):
            raise TypeError('dic({0}) must be a dictionary with Timetable values and keys, not added previously'.format(dic))
        elif any(t.timestep != self.timestep for t in dic.values()):
            raise ValueError('Some of provided Timetables has timestep != {0}'.format(str(self.timestep)))
        elif not isinstance(force_extend, bool):
            raise TypeError('force_extend({0}) must be bool'.format(force_extend))
        if len(dic) == 0:
            return
        if len(dic) != 1:
            for k in dic:
                self.add_timetable({k: dic[k]}, force_extend)
        k = next(iter(dic))
        new_timetable = deepcopy(dic[k])
        if not self._timetables:
            self._timetables[k] = new_timetable
        else:
            new_start = self.global_start
            new_end = self.global_end
            if not force_extend:
                new_timetable.set_start_end(self.global_start, self.global_end)
                self._timetables[k] = new_timetable
            else:
                if new_start > new_timetable.start:
                    new_start = new_timetable.start
                if new_end < new_timetable.end:
                    new_end = new_timetable.end
                for k in self._timetables:
                    self._timetables[k].set_start_end(new_start, new_end)
                new_timetable.set_start_end(new_start, new_end)
                self._timetables[k] = new_timetable
    def clear(self):
        self._timetables.clear()
    def get_timetables(self):
        return deepcopy(self._timetables)
    @property
    def timestep(self):
        return self._timestep
    @property
    def global_start(self):
        if self._timetables:
            elem = next(iter(self._timetables.values()))
            return elem.start
        else:
            return None
    @property
    def global_end(self):
        if self._timetables:
            elem = next(iter(self._timetables.values()))
            return elem.end
        else:
            return None
    def __str__(self):
        return '{0}({1})[{2}-{3} items-{4}]'.format(self.__class__.__name__, self.timestep, self.global_start.strftime('%H:%M') if self._timetables else '(-)', self.global_end.strftime('%H:%M') if self._timetables else '(-)', len(self._timetables))
    def __repr__(self):
        return str(self)
    def __init__(self, timestep, timetables = {}):
        if isinstance(timestep, datetime.time):
            self._timestep = datetime.datetime.combine(datetime.date.min, timestep) - datetime.datetime.min
        elif isinstance(timestep, datetime.timedelta):
            self._timestep = timestep
        else:
            raise TypeError('timestep({0}) must be time or timedelta'.format(timestep.__class__.__name__))
        self._timetables = {}
        self.add_timetable(timetables)

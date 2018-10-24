from .interval import TimetableInterval
from .interval_cursor import TimetableIntervalCursor
from .order import TimetableOrder
from .search import long_sorted_search
from .sort import sorted_insert

from copy import deepcopy, copy
from math import ceil

import datetime


class Timetable:
    '''
    This class is a timetable generator.
    The generated timetable consists of 3 parts: head, opened part, tail.
    This requires 4 separators: start, first, last, end.
        - head - closed intervals, before opened intervals
        - tail - closed intervals, after opened intervals
        - opened part - opened intervals, between 'head' and 'tail'
    The layout:
        [|start|..head..|first|..opened..|last|..tail..|end|]
    The generation is done from the begin.
    So, elements correspond to each part according to their 'start' field.
    The used model is '[start, end)'

    :var timestep: the step of intervals, used as same unit, when combining different timetables (the final interval length is ``timestep * timesteps_num``)
    :var start: readonly, timetable start, always >= ``end`` (use ``set_start_end()``)
    :var end: readonly, timetable end, always <= ``start`` (use ``set_start_end()``)
    :var first: readonly, timetable 'opened' block start, always >= ``last`` (use ``set_first_last()``)
    :var last: readonly, timetable 'opened' block end, always <= ``first`` (use ``set_first_last()``)
    :var timesteps_num: the number of steps to be used in 'opened' intervals (the final interval length is ``timestep * timesteps_num``)
    :var is_open: if timetable does not work, just sets all intervals as unorderable
    :var orders: read-only, all known orders to be spread between TimetableIntervals, can`t overflow each other
    :var show_head_orders: if head must use earlier orders when it doesn`t have the own ones, useful when cropping start
    :type timestep: timedelta
    :type start: datetime
    :type end: datetime
    :type first: datetime
    :type last: datetime
    :type timesteps_num: int (positive)
    :type is_open: bool
    :type orders: list (of ``TimetableOrder``)
    :type show_head_orders: bool
    '''
#
# Add/get/filter/clear orders
#
    def add_order(self, value, to_ordered_interval = lambda v: v):
        if isinstance(value, list) and all(isinstance(to_ordered_interval(o), TimetableOrder) for o in value):
            for v in value:
                # sorted_insert contains integrity assurance
                sorted_insert(self._orders, TimetableOrder, 'start', 'end', to_ordered_interval(v))
        elif isinstance(to_ordered_interval(value), TimetableOrder):
            sorted_insert(self._orders, TimetableOrder, 'start', 'end', to_ordered_interval(value))
        else:
            raise TypeError('value({0}) must be TimetableOrder after to_ordered_interval transformation or list of them'.format(value.__class__.__name__))
    def get_orders(self, interval = None, f_filter = None):
        if f_filter is not None and not callable(f_filter):
            raise TypeError('f_filter({0}) must be callable or None'.format(f_filter.__class__.__name__))
        lst = []
        if not interval:
            # When orders are added, they are no longer belong to user
            lst = deepcopy(self._orders)
        elif isinstance(interval, TimetableInterval):
            # When orders are added, they are no longer belong to user
            lst = deepcopy(long_sorted_search(self._orders, TimetableInterval, 'start', 'end', interval, lst_obj_class = TimetableOrder))
        else:
            raise TypeError('interval({0}) must be TimetableInterval or None'.format(interval.__class__.__name__))
        if f_filter:
            filter(f_filter, lst)
        return lst
    def filter_orders(self, f_filter):
        if not callable(f_filter):
            return
        self._orders = filter(f_filter, self._orders)
    def clear_orders(self):
        self._orders.clear()
#
# Get real start/end and head/opened/tail lengths
#
    def get_first_start(self):
        head_elem_num = self.get_head_len()
        return self.start + self.timestep * head_elem_num
    def get_last_start(self):
        first = self.get_first_start()
        opened_elem_num = (self.last - first) // (self.timestep * self.timesteps_num)
        opened_delta = (self.timestep * self.timesteps_num) * opened_elem_num
        return first + opened_delta
    def get_head_len(self):
        return ceil((self.first - self.start) // self.timestep)
    def get_opened_len(self):
        return (self.get_last_start() - self.get_first_start()) / self.timestep
    def get_tail_len(self):
        return (self.end - self.get_last_start()) // self.timestep
    def get_ending_interval_start(self):
        return self.get_last_start() + self.timestep * self.get_tail_len()
#
# Search for interval
#
    def find_interval(self, dt, now = None, add_orders = True, f_filter = None):
        if not isinstance(dt, datetime.datetime):
            raise TypeError('dt({0}) must be datetime'.format(dt.__class__.__name__))
        elif now is not None and not isinstance(now, datetime.datetime):
            raise TypeError('now({0}) must be datetime or None'.format(now.__class__.__name__))
        elif not isinstance(add_orders, bool):
            raise TypeError('add_orders({0}) must be bool'.format(add_orders.__class__.__name__))
        # Using [start, end)
        if dt < self.start or dt >= self.get_ending_interval_start():
            return None
        # start <= first <= last <= end
        if dt >= self.get_last_start():
            for it in TimetableIntervalCursor(self.get_last_start(), self.timestep, self.end, now = now):
                if it.end > dt:
                    it.is_open = False
                    if add_orders:
                        it.orders = self.get_orders(it, f_filter)
                    return it
        elif dt >= self.get_first_start():
            for it in TimetableIntervalCursor(self.get_first_start(), self.timestep, self.get_last_start(), self.timesteps_num, now = now):
                if it.end > dt:
                    it.is_open = self.is_open
                    if add_orders:
                        it.orders = self.get_orders(it, f_filter)
                    return it
        else:
            for it in TimetableIntervalCursor(self.start, self.timestep, self.get_first_start(), now = now):
                if it.end > dt:
                    it.is_open = False
                    if add_orders:
                        it.orders = self.get_orders(it, f_filter)
                    return it
#
# Gen all!
#
    def gen_head(self, now = None, f_filter = None):
        result = []
        # Required, because true 'first' >= self.first
        last_in_head = self.get_first_start()
        for it in TimetableIntervalCursor(self.start, self.timestep, last_in_head, now = now):
            it.is_open = False
            it.orders = self.get_orders(it, f_filter)
            result.append(it)
        # If flag not set, all is done
        if not self.show_head_orders or not self._orders:
            return result
        # If order exists, an extra-attachment not needed
        for r in result:
            if r.orders:
                return result
        # Else, attach nearest before head
        # (but first, check it is possible)
        if self._orders[0].start >= self.start:
            return result
        order_to_add = None
        for o in self._orders:
            if o.end > self.start:
                break
            elif f_filter:
                if f_filter(o):
                    order_to_add = o
            else:
                order_to_add = o
        if order_to_add:
            result[0].orders = [deepcopy(order_to_add)]
        return result
    def gen_list(self, now = None, f_filter = None):
        result = []
        first_in_opened = self.get_first_start()
        for it in TimetableIntervalCursor(first_in_opened, self.timestep, self.last, self.timesteps_num, now = now):
            it.is_open = self.is_open
            it.orders = self.get_orders(it, f_filter)
            result.append(it)
        return result
    def gen_list_limited(self, limit, usr_field, usr_obj, now = None, f_filter = None):
        def is_ordered(elem, usr_field, usr_obj):
            if not elem.is_open or not elem.orders:
                return False
            for o in elem.orders:
                if not usr_field in o.extra_data:
                    raise ValueError('order({0}) in elem({1}) does not contain \'{2}\' field'.format(o, elem, usr_field))
                if o.extra_data[usr_field] == usr_obj:
                    return True
            return False
        if not limit or not isinstance(limit, int) or limit <= 0:
            raise TypeError('limit({0}) must be int > 0'.format(limit))
        elif not usr_field or not isinstance(usr_field, str):
            raise TypeError('usr_field({0}) must be the field of the \'extra\' Order field'.format(usr_field.__class__.__name__))
        result = self.gen_list(now, f_filter)
        for i in range(len(result)):
            result[i].group_size = 1 if is_ordered(result[i], usr_field, usr_obj) else 0
        i = 0
        while i < len(result):
            if result[i].group_size:
                j = i + 1
                while j < len(result) and result[j].group_size: 
                    j += 1
                result[i].group_size = result[j - 1].group_size = j - i
                i = j
            i += 1
        i = 0
        while i < len(result):
            if not result[i].group_size:
                if i != 0 and i != len(result) - 1 and result[i - 1].group_size and result[i + 1].group_size and 1 + result[i - 1].group_size + result[i + 1].group_size >= limit:
                    result[i].is_open = False
                elif i != 0 and result[i - 1].group_size >= limit:
                    result[i].is_open = False
                elif i != len(result) - 1 and result[i + 1].group_size >= limit:
                    result[i].is_open = False
            i += 1
        return result
    def gen_tail(self, now = None, f_filter = None):
        result = []
        first_in_tail = self.get_last_start()
        for it in TimetableIntervalCursor(first_in_tail, self.timestep, self.end, now = now):
            it.is_open = False
            it.orders = self.get_orders(it, f_filter)
            result.append(it)
        return result
#
# Other properties
#
    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end
    @property
    def first(self):
        if self.start <= self._first and self._first <= self.end:
            return self._first
        else:
            return self._start
    @property
    def last(self):
        if self.start <= self._last and self._last <= self.end:
            return self._last
        else:
            return self.end
    def get_timestep(self):
        return self._timestep
    def set_timestep(self, timestep):
        if isinstance(timestep, datetime.time):
            self._timestep = datetime.datetime.combine(datetime.date.min, timestep) - datetime.datetime.min
        elif isinstance(timestep, datetime.timedelta):
            self._timestep = timestep
        else:
            raise TypeError('timestep({0}) must be time or timedelta'.format(timestep.__class__.__name__))
        return self._timestep
    timestep = property(get_timestep, set_timestep)
    def get_timesteps_num(self):
        return self._timesteps_num
    def set_timesteps_num(self, timesteps_num):
        if not isinstance(timesteps_num, int) or timesteps_num <= 0:
            raise TypeError('timesteps_num({0}) must be int > 0'.format(timesteps_num.__class__.__name__))
        self._timesteps_num = timesteps_num
        return self._timesteps_num
    timesteps_num = property(get_timesteps_num, set_timesteps_num)
    def get_is_open(self):
        return self._is_open
    def set_is_open(self, is_open):
        if not isinstance(is_open, bool):
            raise TypeError('is_open({0}) must be bool'.format(is_open.__class__.__name__))
        self._is_open = is_open
        return self._is_open
    is_open = property(get_is_open, set_is_open)
    def get_show_head_orders(self):
        return self._show_head_orders
    def set_show_head_orders(self, show_head_orders):
        if not isinstance(show_head_orders, bool):
            raise TypeError('show_head_orders({0}) must be bool'.format(show_head_orders.__class__.__name__))
        self._show_head_orders = show_head_orders
        return self._show_head_orders
    show_head_orders = property(get_show_head_orders, set_show_head_orders)
    def set_start_end(self, start, end):
        if not all(isinstance(t, datetime.datetime) for t in [start, end]):
            raise TypeError('start({0}) and end({1}) must be datetime'.format(start.__class__.__name__, end.__class__.__name__))
        elif start > end:
            raise ValueError('need start({0}) > end({1})'.format(start, end))
        self._start = start
        self._end = end
    def set_first_last(self, first, last):
        if not all(isinstance(t, datetime.datetime) for t in [first, last]):
            raise TypeError('first({0}) and last({1}) must be datetime'.format(first.__class__.__name__, last.__class__.__name__))
        elif first > last:
            raise ValueError('need first({0}) > last({1})'.format(first, last))
        self._first = first
        self._last = last
    def __init__(self, timestep,
            start = datetime.datetime.min, 
            end = datetime.datetime.min + datetime.timedelta(days = 1), 
            first = datetime.datetime.min, 
            last = datetime.datetime.min + datetime.timedelta(days = 1), 
            timesteps_num = 1,
            is_open = True,
            show_head_orders = False):
        # Note: 'timestep' can be set as 'time' or 'timedelta',
        #       other args must be set according to the class docstrings
        self.set_start_end(start, end)
        self.set_first_last(first, last)
        self.timestep = timestep
        self.timesteps_num = timesteps_num
        self.is_open = is_open
        self._orders = []
        self.show_head_orders = show_head_orders
    def __str__(self):
        return '{0}({1}x{2})[{3}-{4}-{5}-{6}]'.format(self.__class__.__name__, self.timestep, self.timesteps_num, self.start.strftime('%H:%M'), self.first.strftime('%H:%M') if hasattr(self, 'first') else 'unset', self.last.strftime('%H:%M') if hasattr(self, 'last') else 'unset', self.end.strftime('%H:%M'))
    def __repr__(self):
        return str(self)
    def __len__(self):
        return (self.end - self.start) // (self.timestep * self.timesteps_num)

# This is a module for Timetable class
# This class can be used to generate timetable list - list of datetime intervals
import datetime
# Need ceil()
import math
from copy import deepcopy as copy

def get_datetime_minute_more(value, date_start = None):
    if date_start and not isinstance(date_start, datetime.datetime):
        raise TypeError('Unsupported date_start type {0} must be datetime or time'.format(date_start.__class__))
    if isinstance(value, datetime.time):
        # no seconds and milliseconds in timetable
        hour_minute_only = datetime.time(hour = value.hour, minute = value.minute)
        # got reference date
        if date_start:
            # start time is bigger => +1 day
            #if date_start.time() >= value:
            #    return datetime.datetime.combine((date_start + datetime.timedelta(days = 1)).date(), hour_minute_only)
            #else:
            return datetime.datetime.combine(date_start.date(), hour_minute_only)
        # minimum by default
        else:
            return datetime.datetime.combine(datetime.date.min, hour_minute_only)
    elif isinstance(value, datetime.datetime):
        return datetime.datetime.combine(value.date(), datetime.time(hour = value.time().hour, minute = value.time().minute))
    else:
        raise TypeError('Unsupported value type {0} must be datetime or time'.format(value.__class__))

class OrderedInterval:
    def __init__(self, start, end, extra_data = {}, nid = None):
        start = get_datetime_minute_more(start)
        delta = datetime.timedelta()
        if isinstance(end, datetime.time) and start.time() >= end:
            delta = datetime.timedelta(days = 1)
        end = get_datetime_minute_more(end) + delta
        if start > end:
            raise ValueError('need start({0}) <= end({1})'.format(start, end))
        self.start = start
        self.end = end
        self.id = nid
        self.extra_data = extra_data
    def __str__(self):
        return '{0}({1}-{2})'.format(self.__class__.__name__, self.start.strftime('%H:%M'), self.end.strftime('%H:%M'))
    def __repr__(self):
        return str(self)

class TimetableElement:
    def __init__(self, start, end, is_open = True, timesteps_num = 1, orders = []):
        start = get_datetime_minute_more(start)
        end = get_datetime_minute_more(end)
        if start > end:
            raise ValueError('need start({0}) <= end({1})'.format(start, end))
        self.start = start
        self.end = end
        self.is_open = is_open
        self.timesteps_num = timesteps_num
        if orders is not None and not isinstance(orders, list) and not all( isinstance(o, OrderedInterval) for o in orders):
            raise TypeError('orders({0}) must be type a list of OrderedInterval'.format(orders.__class__.name__))
        self.orders = []
    def __str__(self):
        return '({0}-{1} {2}{3})'.format(self.start.strftime('%H:%M'), self.end.strftime('%H:%M'), 'opened' if self.is_open else 'closed', ' orders={0}'.format(str(self.orders)) if self.orders else '')
    def __repr__(self):
        return str(self)


class TimeIntervalCursor:
    def __init__(self, start, timestep, stop, timesteps_num = 1):
        if not isinstance(start, datetime.datetime) or not isinstance(timestep, datetime.timedelta) or not isinstance(stop, datetime.datetime):
            raise TypeError('need start({0}) = datetime and timestep({1}) = timedelta and stop({2}) = datetime'.format(start.__class__.__name__, timestep.__class__.__name__, stop.__class__.__name__))
        self.start = start
        self.end = start + timestep*timesteps_num
        self.timestep = timestep
        self._stop = stop
        self.timesteps_num = timesteps_num
    def __iter__(self):
        return self
    def __next__(self):
        if self.end > self._stop:
            raise StopIteration
        else:
            to_ret = TimetableElement(self.start, self.end, timesteps_num = self.timesteps_num)
            self.start = self.end
            self.end += self.timestep*self.timesteps_num
            return to_ret

class Timetable:
    _max_days = 1 # timetable is for 1 day by default
    _ordered_lst = []
    # default value for gen_list()
    is_open = True
    def add_ordered(self, value, to_ordered_interval = lambda v: v):
        if not isinstance(value, list) and isinstance(to_ordered_interval(value), OrderedInterval):
            order = to_ordered_interval(value)
            i = 0
            not_done = True
            for i in range(0, len(self._ordered_lst)):
                if self._ordered_lst[i].start >= order.end:
                    if i != 0 and self._ordered_lst[i - 1].end > order.start:
                        raise ValueError('Can`t insert {0} between {1} and {2}'.format(order, self._ordered_lst[i - 1], self._ordered_lst[i]))
                    not_done = False
                    self._ordered_lst.insert(i, order)
                    break
            if not_done:
                self._ordered_lst.append(order)
        elif isinstance(value, list) and all(isinstance(to_ordered_interval(v), OrderedInterval) for v in value):
            for v in value:
                self.add_ordered(v, to_ordered_interval)
        else:
            raise TypeError('order({0}) must be type OrderedInterval or a list of them'.format(value.__class__.__name__))
    def _get_orders(self, interval):
        if not self._ordered_lst:
            return []
        elif self._ordered_lst[0].start >= interval.end or self._ordered_lst[-1].end <= interval.start:
            return []
        start_i = 0
        end_i = len(self._ordered_lst)
        result = []
        # Binary search of some orders, that correspond to 'interval'
        while start_i != end_i:
            middle = (start_i + end_i) // 2
            #0...|inter|.....N
            #0..#ord#........N
            if (self._ordered_lst[middle].start <= interval.start 
                    and interval.start < self._ordered_lst[middle].end):
                #print('Toggle 1, i = {0} = {1}'.format(middle, self._ordered_lst[middle]))
                start_i = end_i = middle
                break
            #0...|inter|.....N
            #0.......#ord#...N
            if (self._ordered_lst[middle].start < interval.end
                    and interval.end <= self._ordered_lst[middle].end):
                #print('Toggle 2, i = {0} = {1}'.format(middle, self._ordered_lst[middle]))
                start_i = end_i = middle
                break
            #0...|inter|.....N
            #0.#long_order#.N
            if (interval.start >= self._ordered_lst[middle].start
                    and self._ordered_lst[middle].end >= interval.end):
                #print('Toggle 3, i = {0} = {1}'.format(middle, self._ordered_lst[middle]))
                start_i = end_i = middle
                break
            if interval.end <= self._ordered_lst[middle].start:
                #print('i={0} - to end_i({1},{2}) - Changed interval.end({3}) <= order.start({4})'.format(middle, start_i,end_i,interval, self._ordered_lst[middle]))
                if end_i - start_i == 1:
                    end_i -= 1
                else:
                    end_i = middle
            else:
                #print('i={0} - to end_i({1},{2}) - Changed interval.end({3}) vs order.start({4})'.format(middle, start_i,end_i,interval, self._ordered_lst[middle]))
                if end_i - start_i == 1:
                    start_i += 1
                else:
                    start_i = middle
        #print('final i = {0}'.format(start_i))
        result.append(self._ordered_lst[start_i])
        # Find possible before
        i = start_i
            #0...|inter|.....N
            #0...#ord#ord#...N
        if i != 0 and self._ordered_lst[i - 1].end > interval.start:
            #print('# go left')
            while i != 0:
                if self._ordered_lst[i - 1].end <= interval.start:
                    break
                #print('add i = {0} = {1}'.format(i - 1, self._ordered_lst[i - 1]))
                result.insert(0, self._ordered_lst[i - 1])
                i -= 1
        # Find possible after
        i = start_i
            #0....|inter|....N
            #0..#ord#ord#....N
        if i != len(self._ordered_lst) - 1 and self._ordered_lst[i + 1].start < interval.end:
            #print('# go right')
            while i != len(self._ordered_lst) - 1:
                if self._ordered_lst[i + 1].start >= interval.end:
                    break
                #print('add i = {0} = {1}'.format(i + 1, self._ordered_lst[i + 1]))
                result.append(self._ordered_lst[i + 1])
                i += 1
        return result
    def _get_first_element(self):
        return self.start + self.timestep * math.ceil((self.first - self.start) / self.timestep)
    def _get_last_element(self):
        first = self._get_first_element()
        head_delta = first - self.start
        body_delta = (self.timestep * self.timesteps_per_order) * ((self.last - (self.start + head_delta)) // (self.timestep * self.timesteps_per_order))
        return first + body_delta
    def get_head_len(self):
        return (self._get_first_element() - self.start) / self.timestep
    def get_list_len(self):
        return (self._get_last_element() - self._get_first_element()) / self.timestep
    def get_tail_len(self):
        return (self.end - self._get_last_element()) / self.timestep
    def gen_list(self):
        if not self.is_ready():
            raise AttributeError('Need set start({0}) <= first({1}) <= last({2}) <= end({3})'.format(self.start, self.first, self.last, self.end))
        result = []
        first_elem = self._get_first_element()
        for it in TimeIntervalCursor(first_elem, self.timestep, self.last, self.timesteps_per_order):
            it.orders = self._get_orders(it)
            it.is_open = self.is_open
            result.append(it)
        return result
    def gen_head(self):
        if not self.is_ready():
            raise AttributeError('Need set start({0}) <= first({1}) <= last({2}) <= end({3})'.format(self.start, self.first, self.last, self.end))
        last_elem = self._get_first_element()
        result = []
        for it in TimeIntervalCursor(self.start, self.timestep, last_elem):
            it.is_open = False
            it.orders = self._get_orders(it)
            result.append(it)
        return result
    def gen_tail(self):
        if not self.is_ready():
            raise AttributeError('Need set start({0}) <= first({1}) <= last({2}) <= end({3})'.format(self.start, self.first, self.last, self.end))
        tail_start = self._get_last_element()
        result = []
        for it in TimeIntervalCursor(tail_start, self.timestep, self.end):
            it.is_open = False
            it.orders = self._get_orders(it)
            result.append(it)
        return result
    def clear_ordered(self):
        self._ordered_lst.clear()
    # _first = datetime.datetime
    # _last = datetime.datetime
    # _start = datetime.datetime
    # _end = datetime.datetime
    # _timestep = datetime.timedelta
    # _timesteps_per_order = int > 0
    def is_ready(self):
        if not all(hasattr(self, attr) for attr in
            ['_first', '_last', '_start', '_end',
                '_timestep', '_timesteps_per_order']):
            return False
        elif not (self.start <= self.first and self.first <= self.last
                and self.last <= self.end):
            return False
        else:
            return True
    def set_date(self, date):
        if not self.is_ready():
            raise AttributeError('This object is not ready!')
        else:
            tmp = Timetable(timestep = self.timestep, timesteps_per_order = self.timesteps_per_order)
            tmp_start = datetime.datetime.combine(date, self.start.time())
            tmp_end = tmp_start + (self.end - self.start)
            tmp.set_start_end(tmp_start, tmp_end)
            tmp_first = datetime.datetime.combine(date, self._first.time())
            tmp_last = tmp_first + (self._last - self._first)
            tmp.set_first_last(tmp_first, tmp_last)
            # No errors found & the object is safe
            self.set_start_end(tmp_start, tmp_end)
            self.set_first_last(tmp_first, tmp_last)
    def _set_timestep(self, timestep):
        if any(isinstance(timestep, t) for t in [datetime.timedelta, datetime.time, datetime.datetime]):
            if isinstance(timestep, datetime.timedelta):
                timestep = get_datetime_minute_more(datetime.datetime.min + timestep) - datetime.datetime.min
            else:
                timestep = get_datetime_minute_more(timestep) - datetime.datetime.min
            if timestep > datetime.timedelta(days = self._max_days):
                raise ValueError('need timestep({0}) <= _max_days({1})'.format(timestep, self._max_days))
            self._timestep = timestep
        else:
            raise TypeError('timestep must be timedelta, time or datetime')
    @property
    def timestep(self):
        """get timestep, the timetable datetime quantum"""
        return self._timestep
    def set_timesteps_per_order(self, value):
        if isinstance(value, int):
            if  value > 0:
                if hasattr(self, '_timestep') and self.timestep*value > datetime.timedelta(days = self._max_days):
                    raise ValueError('need timestep({0})*per_order({1}) <= _max_days({2})'.format(self.timestep, value, self._max_days))
                self._timesteps_per_order = value
            else:
                raise ValueError('need timesteps_per_order{0} > 0'.format(value))
        else:
            raise TypeError('timesteps_per_order must be integer')
    def get_timesteps_per_order(self):
        """get timesteps per single order"""
        return self._timesteps_per_order
    timesteps_per_order = property(get_timesteps_per_order, set_timesteps_per_order, doc = 'timetable timesteps_per_order positive int')
    def set_start(self, value):
        if isinstance(value, datetime.time) or isinstance(value, datetime.datetime):
            start = get_datetime_minute_more(value)
            if hasattr(self, '_end'):
                if start > self.end:
                    raise ValueError('need start({0}) < end({1})'.format(start, self.end))
                elif self.end - start > datetime.timedelta(days = self._max_days):
                    raise ValueError('need [end-start]({0}) < _max_days({1})'.format(str(self.end - start), self._max_days))
            self._start = start
        else:
            raise TypeError('start must be time or datetime')
    def get_start(self):
        return self._start
    start = property(get_start, set_start, doc = 'timetable start datetime')
    def set_end(self, value):
        if isinstance(value, datetime.time):
            self._end = get_datetime_minute_more(value)
            if hasattr(self, '_start') and value <= self.start.time():
                self._end += datetime.timedelta(days = 1)
        elif isinstance(value, datetime.datetime):
            if (hasattr(self, '_start') and value - self.start <= datetime.timedelta(days = self._max_days)) or value - datetime.datetime.min <= datetime.timedelta(days = self._max_days):
                self._end = get_datetime_minute_more(value)
            else:
                return ValueError('end must be contain days <= {0} or (end - start) <= {0}'.format(self._max_days))
        else:
            raise TypeError('end must be set as time or datetime')
    def get_end(self):
        return self._end
    end = property(get_end, set_end, doc = 'timetable end datetime')
    def set_start_end(self, start, end):
        types = [datetime.time, datetime.datetime]
        if all(any(isinstance(startend, t) for t in types) for startend in [start, end]):
            delta = datetime.timedelta()
            if all(isinstance(t, datetime.time) for t in [start, end]) and start >= end:
                delta = datetime.timedelta(days = 1)
            start = get_datetime_minute_more(start)
            end = get_datetime_minute_more(end) + delta
            if start > end:
                raise ValueError('need start <= end')
            elif start - end > datetime.timedelta(days = self._max_days):
                raise ValueError('need start({0}) - last({1}) <= {2} days'.format(start, end, self._max_days))
            else:
                self._start = start
                self._end = end
        else:
            TypeError('need start({0}) and end({0}) to be datetime or time'.format(start.__class__.__name__, end.__class__.name__))
    def set_first_last(self, first, last):
        types = [datetime.time, datetime.datetime]
        if all(any(isinstance(se, t) for t in types) for se in [first, last]):
            delta = datetime.timedelta()
            if all(isinstance(t, datetime.time) for t in [first, last]) and first >= last:
                delta = datetime.timedelta(days = 1)
            first = get_datetime_minute_more(first, self.start)
            last = get_datetime_minute_more(last, self.start) + delta
            if first > last:
                raise ValueError('need first <= last')
            else:
                self._first = first
                self._last = last
        else:
            TypeError('need first({0}) and last({0}) to be datetime or time'.format(first.__class__.__name__, last.__class__.name__))
    def set_first(self, value):
        if not hasattr(self, '_start') or not hasattr(self, '_end'):
            raise AttributeError('start and end must be set first')
        if isinstance(value, datetime.time) or isinstance(value, datetime.datetime):
            first = get_datetime_minute_more(value, self.start)
            if hasattr(self, '_last') and first > self._last:
                raise ValueError('need first <= last')
            self._first = first
        else:
            raise TypeError('first must be set as time or datetime')
    def get_first(self):
        if self.start <= self._first and self._first <= self.end:
            return self._first
        elif self.start > self._first:
            return self.start
        else:
            return self.end
    first = property(get_first, set_first, doc = 'timetable first datetime')
    def set_last(self, value):
        if not hasattr(self, '_start') or not hasattr(self, '_end'):
            raise AttributeError('start and end must be set first')
        if isinstance(value, datetime.time) or isinstance(value, datetime.datetime):
            last = get_datetime_minute_more(value, self.start)
            if hasattr(self, '_first') and self._first >= last:
                if isinstance(value, datetime.time):
                    last += datetime.timedelta(days = 1)
                    if self._first > last:
                        raise ValueError('need first <= last')
                else:
                    raise ValueError('need first <= last')
            self._last = last
        else:
            raise TypeError('first must be set as time or datetime')
    def get_last(self):
        if self.start <= self._last and self._last <= self.end:
            return self._last
        elif self.start > self._last:
            return self.start
        else:
            return self.end
    last = property(get_last, set_last, doc = 'timetable last datetime')
    def __init__(self, timestep, 
            start = datetime.datetime.min, 
            end = datetime.datetime.min + datetime.timedelta(days = 1), 
            first = datetime.datetime.min, 
            last = datetime.datetime.min + datetime.timedelta(days = 1), 
            timesteps_per_order = 1,
            is_open = True):
        self._set_timestep(timestep)
        self.set_timesteps_per_order(timesteps_per_order)
        self.set_start_end(start, end)
        self.set_first_last(first, last)
        self._max_days = 1 # timetable is for 1 day by default
        self._ordered_lst = []
        self.is_open = is_open
    def __str__(self):
        return '{0}[{1}-{2}-{3}-{4}]'.format(self.__class__.__name__, self.start.strftime('%H:%M'), self.first.strftime('%H:%M') if hasattr(self, 'first') else 'unset', self.last.strftime('%H:%M') if hasattr(self, 'last') else 'unset', self.end.strftime('%H:%M'))
    def __repr__(self):
        return str(self)
    def __len__(self):
        return (self.end - self.start) // (self.timestep * self.timesteps_per_order)

class TimetableList:
    _max_days = 1 # timetable is for 1 day by default
    _timetables = {}
    _final_start = None
    _final_end = None
    def crop_time_start(self, new_start, leave_closed_cells_num = 0):
        if isinstance(new_start, datetime.time):
            add_to_start = datetime.timedelta()
            if self._final_start.time() >= new_start:
                add_to_start = datetime.timedelta(days = 1)
            new_start = datetime.datetime.combine(self._final_start, new_start) + add_to_start
        elif not isinstance(new_start, datetime.datetime):
            raise TypeError('new_start({0}) must be datetime or time'.format(new_start.__class__.__name__))
        elif not (isinstance(leave_closed_cells_num, int) and leave_closed_cells_num >= 0):
            raise TypeError('leave_closed_cells_num({0}) must be positive integer'.format(leave_closed_cells_num.__class__.__name__))
        # Clear if new_start is after end
        if new_start > self._final_end:
            self._final_start = self._final_end
            for k in self._timetables:
                self._timetables[k].set_start(self._final_end)
            return
        elif new_start < self._final_start:
            return
        elif not (self._final_start <= new_start and new_start <= self._final_end):
            raise ValueError('need final_start({0}) < news_start({1}) < final_end({2})'.format(self._final_start, new_start, self._final_end))
        saved_cells_num = math.ceil((new_start - self._final_start)/self.timestep)
        start = self._final_start + self.timestep*saved_cells_num
        first = start
        if (start - self._final_start) / self.timestep < leave_closed_cells_num:
            leave_closed_cells_num = (start - self._final_start) / self.timestep
        if saved_cells_num >= leave_closed_cells_num:
            start -= self.timestep*leave_closed_cells_num
        for k in self._timetables:
            self._timetables[k].set_start(start)
            self._timetables[k].set_first(first)
        self._final_start = start
    def clear_closed_rows(self):
        if not self._timetables:
            return
        # head
        min_len = None
        for k in self._timetables:
            l = self._timetables[k].get_head_len()
            if min_len is None or l < min_len:
                min_len = l
        start = self._final_start + self.timestep*min_len
        for k in self._timetables:
            self._timetables[k].set_start(start)
        self._final_start = start
        # tail
        min_len = None
        for k in self._timetables:
            l = self._timetables[k].get_tail_len()
            if min_len is None or l < min_len:
                min_len = l
        end = self._final_end - self.timestep*min_len
        for k in self._timetables:
            self._timetables[k].set_end(end)
        self._final_end = end
    def get_timetables(self):
        return self._timetables.copy()
    def clear(self):
        self._timetables.clear()
        self._final_start = self._final_end = None
    @property
    def timestep(self):
        """get timestep, the timetable datetime quantum"""
        return self._timestep
    @property
    def final_start(self):
        """get working start time"""
        return self._final_start
    @property
    def final_end(self):
        """get working end time"""
        return self._final_end
    def _set_timestep(self, timestep):
        if any(isinstance(timestep, t) for t in [datetime.timedelta, datetime.time, datetime.datetime]):
            if isinstance(timestep, datetime.timedelta):
                timestep = get_datetime_minute_more(datetime.datetime.min + timestep) - datetime.datetime.min
            else:
                timestep = get_datetime_minute_more(timestep) - datetime.datetime.min
            if timestep > datetime.timedelta(days = self._max_days):
                raise ValueError('need timestep({0}) <= _max_days({1})'.format(timestep, self._max_days))
            self._timestep = timestep
        else:
            raise TypeError('timestep must be timedelta, time or datetime')
    # 'dic' is a { 'Service name': Timetable }
    def add_timetable(self, dic, force_extend = False):
        if isinstance(dic, dict) and all(isinstance(k, str) for k in dic) and all(isinstance(t, Timetable) for t in dic.values()):
            #print('input {0} vs stored {1}'.format(str(list(k for k in dic)), str(list(k for k in self._timetables))))
            if any(k in self._timetables for k in dic):
                raise ValueError('Some keys already used:\n- Stored:     {0}\n- Candidates: {1}'.format(str(self._timetables), str(dic)))
            if len(dic) == 1:
                #print('got single {0}'.format(str(dic)))
                k = next(iter(dic))
                if not self._timetables:
                    self._timetables[k] = copy(dic[k])
                    self._final_start = copy(dic[k].start)
                    self._final_end = copy(dic[k].end)
                else:
                    if not force_extend:
                        val = copy(dic[k])
                        val.set_start_end(self.final_start, self.final_end)
                        self._timetables[k] = val
                    else:
                        #print('having start({0}) and end({1})'.format(self.final_start, self.final_end))
                        new_start = self.final_start
                        new_end = self.final_end
                        if new_start > dic[k].start:
                            new_start = copy(dic[k].start)
                        if new_end < dic[k].end:
                            new_end = copy(dic[k].end)
                        for key in self._timetables:
                            self._timetables[key].set_start_end(new_start, new_end)
                        val = copy(dic[k])
                        val.set_start_end(new_start, new_end)
                        self._timetables[k] = val
                        self._final_start = new_start
                        self._final_end = new_end
            else:
                for k in dic:
                    self.add_timetable({k: dic[k]}, force_extend)
        else:
            raise TypeError('dic({0}) must be dict with keys = str and values = Timetable'.format(dic.__class__.__name__))
    def __str__(self):
        return '{0}[{1}-{2} items-{3}]'.format(self.__class__.__name__, self.final_start.strftime('%H:%M'), len(self._timetables), self.final_end.strftime('%H:%M'))
    def __repr__(self):
        return str(self)
    def __init__(self, timestep):
        self._max_days = 1 # timetable is for 1 day by default
        self._timetables = {}
        self._final_start = None
        self._final_end = None
        self._set_timestep(timestep)

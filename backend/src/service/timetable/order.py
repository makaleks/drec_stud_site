from .util import adjust_start_end


class TimetableOrder:
    '''
    This class is a container for any orders in Timetable.

    :var start: readonly, order start, always >= ``end`` (use ``set_start_end()``)
    :var end: readonly, order end, always <= ``start`` (use ``set_start_end()``)
    :var extra_data: optional (default=``{}``), used to attach any data to order
    :var id: optional (default=``None``), used to link with the user order id
    :type start: datetime
    :type end: datetime
    :type extra_data: object
    :type id: object
    '''
    def __init__(self, start, end, extra_data = {}, nid = None):
        '''
        Initializes the ``TimetableOrder``.
        In case just the ``time`` provided and ``start`` > ``end``, the ``end`` will have ``+1`` day.

        :param start: order start
        :param end: order end
        :param extra_data: optional (default=``{}``), used to attach any data to order
        :param id: optional (default=``None``), used to link with the user order id
        :type start: datetime, time (same as ``end``)
        :type end: datetime, time (same as ``start``)
        :type extra_data: object
        :type id: object

        .. warning:: In case just the ``time`` provided and ``start`` > ``end``, the ``end`` will have ``+1`` day.
        '''
        self.set_start_end(start, end)
        self.id = nid
        self.extra_data = extra_data
    def __str__(self):
        return '{0}({1}-{2})'.format(self.__class__.__name__, self.start.strftime('%H:%M'), self.end.strftime('%H:%M'))
    def __repr__(self):
        return str(self)
    # These fields are readonly to disable setting 'start' 
    # and 'end' independently
    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end
    def set_start_end(self, start, end):
        start_end = adjust_start_end(start, end)
        self._start = start_end[0]
        self._end = start_end[1]


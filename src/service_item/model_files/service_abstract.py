from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericRelation
from precise_bbcode.fields import BBCodeTextField

import datetime

from service_base.models import ServiceBase

from .working_time import WorkingTime, WorkingTimeException, get_working_time_query, get_working_time_exception_query
from .timetable import Timetable, TimetableList, TimetableOrder
from ..utils import to_dt

# Create your models here.

class ServiceItemAbstract(ServiceBase):
    announcements = BBCodeTextField(blank = True, null = True, verbose_name = 'Объявления')
    # Ordering
    max_continuous_orders = models.PositiveSmallIntegerField(blank = False, null = False, default = 2, verbose_name = 'Максимум непрерывных заказов одного предмета')
    days_to_show          = models.PositiveSmallIntegerField(default = 3, validators = [MinValueValidator(1)], blank = False, null = False, verbose_name = 'Дней на заказ')
    # Timetable
    timestep                = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
    default_works_from      = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени по-умолчанию')
    default_works_to        = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Конец рабочего времени по-умолчанию')
    time_after_now          = models.TimeField(blank = False, null = False, default = datetime.time(0,20,0), verbose_name = 'Времени на запись после начала')
    working_times           = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    is_finished_hidden      = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Скрывать прошедшие интервалы')
    # Entrance
    time_margin_start = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Время на вход до заказа')
    time_margin_end   = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Время на вход после заказа')
    disable_lock      = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'ОТКЛЮЧИТЬ ЗАМКИ')
    def get_time_margin_start(self):
        t = self.time_margin_start
        if t == datetime.time.min:
            return None
        result = ''
        if t.hour:
            result += '{}ч.'.format(str(t.hour))
        if t.minute:
            result += '{}м.'.format(str(t.minute))
        if t.second:
            result += '{}с.'.format(str(t.second))
        return result
    def get_time_margin_end(self):
        t = self.time_margin_end
        if t == datetime.time.min:
            return None
        result = ''
        if t.hour:
            result += '{}ч.'.format(str(t.hour))
        if t.minute:
            result += '{}м.'.format(str(t.minute))
        if t.second:
            result += '{}с.'.format(str(t.second))
        result = ''
        return result
    # Returns { 'works_from', 'works_to', 'is_weekend', 'is_exception' }
    # 'is_exception' means that Item can apply only its own exceptions
    # or None if not working
    def get_working_time(self, day):
        # is_active is immediate
        if not self.is_active:
            return None
        if isinstance(day, datetime.datetime):
            day = day.date()
        if not isinstance(day, datetime.date):
            raise TypeError('day must be datetime.date')
        # PRIORITY (extended: see Item): Service[default] <
        # < Service[working_time] < Service[exception]

        # exception
        wte_service = get_working_time_exception_query(self, day)
        if wte_service.exists():
            exception = wte_service.first()
            dt = to_dt(day, exception.works_from, exception.works_to)
            return {'works_from': dt['start'],
                    'works_to': dt['end'],
                    'is_weekend': exception.is_weekend,
                    'is_exception': True}
        # working_time
        wt_service = get_working_time_query(self, day)
        if wt_service.exists():
            working_time = wt_service.first()
            dt = to_dt(day, working_time.works_from, working_time.works_to)
            return {'works_from': dt['start'],
                    'works_to': dt['end'],
                    'is_weekend': working_time.is_weekend,
                    'is_exception': False}
        # default
        dt = to_dt(day, self.default_works_from, self.default_works_to)
        return {'works_from': dt['start'],
                'works_to': dt['end'],
                'is_weekend': False,
                'is_exception': False}
    # Returns {'date','datestr',
    #   'is_weekend': bool,
    #   'items': {'name': {
    #                       'is_open','rowspan',
    #                       'time':[TimetableInterval]
    #                     }
    #            }
    #   'timetable': [TimetableInterval]
    # }
    # or None if not working
    def get_timetable(self, date, user):
        # is_active is immediate
        if not self.is_active:
            return None
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        s = '{0} {1}'.format(weekdays[date.weekday()], date.strftime('%d.%m'))
        service_working_time = self.get_working_time(date)
        if service_working_time['is_weekend']:
            return {'date': s, 'is_weekend': True, 'items': None, 'timetable': None}
        timetables = TimetableList(self.timestep)
        # key = '' means 'service timetable' => it will be ignored
        service_timetable = Timetable(self.timestep, 
                start = service_working_time['works_from'],
                first = service_working_time['works_from'],
                last = service_working_time['works_to'],
                end = service_working_time['works_to']
            )
        #print(' Adding service {0}'.format(service_timetable))
        timetables.add_timetable({'': service_timetable})
        for t in list(self.items.all()):
            #print('# Next')
            item_timetable_info = t.get_timetable(date)
            if not t.is_active or item_timetable_info['is_weekend']:
                #print('weekend')
                item_timetable = service_timetable
                item_timetable.is_open = False
            else:
                #print('own for {0}'.format(t.name))
                item_timetable = item_timetable_info['timetable']
            #print(item_timetable)
            #print(' Adding {0}'.format(item_timetable))
            timetables.add_timetable({t.name: item_timetable}, item_timetable_info['is_exception'] if item_timetable_info else False)
        # Start check if all items are closed
        is_not_all_weekend = False
        # need to be called, because the result uses copy()
        final_timetables = timetables.get_timetables()
        for k in final_timetables:
            #if k:
            #    print(str(final_timetables[k].is_open))
            if k and final_timetables[k].is_open:
                is_not_all_weekend = True
                break
        if not is_not_all_weekend:
            return {'date': s, 'is_weekend': True, 'items': None, 'timetable': None}
        # End check if all items are closed
        timetables.clear_closed_rows()
        #print(str(timetables._timetables))
        #print(timetables)
        #print(final_timetables)
        final_timetables = timetables.get_timetables()
        #for t in final_timetables.values():
        #    print('Stored start({0}) and end({1})'.format(t.start, t.end))
        now = datetime.datetime.now()
        if self.is_finished_hidden and date == now.date():
            timetables.crop_start(now, leave_head_cell = True, floor_crop = True)
        final_timetables = timetables.get_timetables()
        result = {'date': s, 'is_weekend': False, 'items': {}}
        # Database needs to order properly
        for it in list(self.items.all()):
            t = final_timetables[it.name]
            lst = t.gen_head(now)
            lst.extend(t.gen_list_limited(self.max_continuous_orders, 'user', user, now))
            lst.extend(t.gen_tail(now))
            result['items'][it.name] = {'is_open': t.is_open, 'rowspan': t.timesteps_num, 'time': lst}
            extra_data = it.get_timetable_extra_data()
            result['items'][it.name].update(extra_data)
        lst = final_timetables[''].gen_head(now)
        lst.extend(final_timetables[''].gen_list(now))
        lst.extend(final_timetables[''].gen_tail(now))
        result['timetable'] = lst
        return result
    # Return [{'date','datestr',
    #   'is_weekend': bool,
    #   'items': {'name': ...}
    # }]
    # or None if not working
    def gen_timetable_layout(self, user):
        # is_active is immediate
        if not self.is_active:
            return None
        result = []
        now = datetime.datetime.now().date()
        for i in range(self.days_to_show):
            result.append(self.get_timetable(now + datetime.timedelta(days = i), user))
        return result
    class Meta:
        abstract = True


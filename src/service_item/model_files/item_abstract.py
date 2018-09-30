from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator

from precise_bbcode.fields import BBCodeTextField

import datetime

from utils.model_aliases import DefaultImageField

from .working_time import WorkingTime, WorkingTimeException, get_working_time_query, get_working_time_exception_query
from .timetable import Timetable, TimetableList, TimetableOrder

# Return database filter to ServiceAbstract

def get_children_for_service_item():
    pass

# Create your models here.

class ItemAbstract(models.Model):
    # 'id' field will be added automatically 
    name        = models.CharField(max_length = 64, unique = True, blank = False, null = False, verbose_name = 'Название/номер')
    t_steps_per_order   = models.PositiveSmallIntegerField(default = 1, 
            validators = [MinValueValidator(1)],
            blank = False, null = False, verbose_name = 'Число шагов времени на заказ')
    extra_info  = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Доп. информация')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    created     = models.DateTimeField(auto_now_add = True, null = False, verbose_name = 'Введено в строй')
    working_times       = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    # define your own 'service' field with related_name = 'items'!
    # example:
    # service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    service = None

    def get_price(self):
        return 0
    # Return { 'works_from', 'works_to', 'is_weekend', 'is_exception' }
    # or None if not working
    # All 'works_*' are datetimes
    # 'is_exception' means that Item can apply only its own exceptions
    def get_working_time(self, day, service_working_time = None):
        # is_active is immediate
        if not self.is_active or not self.service.is_active:
            return None
        if isinstance(day, datetime.datetime):
            day = day.date()
        if not isinstance(day, datetime.date):
            raise TypeError('day must be datetime.date')
        # PRIORITY: Service[default] < Service[working_time] < 
        # < Item[working_time] < Service[exception] < Item[exception]

        # item working_time_exceptions
        item_result = service_result = {}
        wte_item = get_working_time_exception_query(self, day)
        if wte_item.exists():
            exception = wte_item.first()
            dt = to_dt(day, exception.works_from, exception.works_to)
            return {'works_from': dt['start'],
                    'works_to': dt['end'],
                    'is_weekend': exception.is_weekend,
                    'is_exception': True}
        # get service working_time
        if not service_working_time:
            service_working_time = self.service.get_working_time(day)
        # service exception is more important 
        # than item`s regular working_time
        if service_working_time['is_exception']:
            return service_working_time
        # item working_times
        wt_item = get_working_time_query(self, day)
        if wt_item.exists() and not item_result:
            working_time = wt_item.first()
            dt = to_dt(day, working_time.works_from, working_time.works_to)
            return {'works_from': dt['start'],
                    'works_to': dt['end'],
                    'is_weekend': working_time.is_weekend,
                    'is_exception': False}
        # if no special for item, return service results
        return service_working_time
    # Return { 'date':         str(%d.%m),
    #          'is_weekend':   bool,
    #          'timetable':    Timetable(start=first, end=last)
    #          'is_exception': bool }
    # or None if not working
    def get_timetable(self, date):
        # is_active is immediate
        if not self.is_active:
            return None
        extra_data = self.get_timetable_extra_data()
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        working_time = self.get_working_time(date)
        s = '{0} {1}'.format(weekdays[date.weekday()], date.strftime('%d.%m'))
        #print('# Item start')
        #print(str(working_time))
        if not working_time or working_time['is_weekend']:
            result = {'date': s, 
                    'is_weekend': True, 'timetable': None, 
                    'is_exception': True}
            result.update(extra_data)
            return result
        timetable = Timetable(
            timestep = self.service.timestep,
            start = working_time['works_from'], 
            end = working_time['works_to'],
            first = working_time['works_from'], 
            last = working_time['works_to'],
            timesteps_num = self.t_steps_per_order)
        raw_orders = list(self.orders.model.get_queryset(working_time['works_from'], working_time['works_to']).filter(item = self))
        timetable.add_order(raw_orders, 
                lambda o: TimetableOrder(
                    start = datetime.datetime.combine(o.date_start,
                        o.time_start),
                    end = datetime.datetime.combine(o.date_start,
                        o.time_end) + datetime.timedelta(days = 1 if o.time_start >= o.time_end else 0),
                    nid = o.pk,
                    extra_data = {'user': o.user}
                )
            )
        #print('# Item end')
        result = {'date': s,
                'is_weekend': False, 'timetable': timetable,
                'is_exception': working_time['is_exception']}
        result.update(extra_data)
        return result

    # Use subclasses to send more data, like 'price'
    # Returns {extra_data_name: extra_data_value,}
    def get_timetable_extra_data(self):
        return {}
    def __str__(self):
        return self.name
    class Meta:
        abstract = True


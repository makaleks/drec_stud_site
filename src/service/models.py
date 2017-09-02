# coding: utf-8
# NOTE: all times use the pattern [X, Y)
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import datetime

# Create your models here.

# Set working hours on each weekday
class WorkingTime(models.Model):
    MONDAY      = 1
    TUESDAY     = 2
    WEDNESDAY   = 3
    THURSDAY    = 4
    FRIDAY      = 5
    SATURDAY    = 6
    SUNDAY      = 7
    EVERYDAY    = 8
    weekday     = models.PositiveSmallIntegerField(default = EVERYDAY, null = False, blank = False, verbose_name = 'Рабочее время', choices = (
            (MONDAY, 'Понедельник'),
            (TUESDAY, 'Вторник'),
            (WEDNESDAY, 'Среда'),
            (THURSDAY, 'Четверг'),
            (FRIDAY, 'Пятница'),
            (SATURDAY, 'Суббота'),
            (SUNDAY, 'Воскресенье'),
            (EVERYDAY, 'Ежедневно'),
        )
    )
    works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени')
    works_to    = models.TimeField(blank = False, null = False, default = datetime.time(23,59,59), verbose_name = 'Конец рабочего времени')
    weekend     = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Выходной')
    description = models.CharField(max_length = 64, blank = True, null = True, verbose_name = 'Описание')
    # Set possible only to Item & Service
    content_type    = models.ForeignKey(
            ContentType, 
            on_delete = models.CASCADE, 
            limit_choices_to = 
                models.Q(app_label = 'service', model = 'service') 
                | models.Q(app_label = 'service', model = 'item'), 
            blank = False, null = False, verbose_name = 'Тип назначения'
        )
    object_id       = models.PositiveIntegerField(blank = False, null = False, verbose_name = 'Id назначения')
    # Enables to set 'content_type' and 'object_id' by assigning
    # the destination object to this field:
    service_or_item = GenericForeignKey('content_type', 'object_id')
    class Meta:
        verbose_name        = 'Время работы'
        verbose_name_plural = 'Расписания'
        ordering            = ['object_id', 'weekday', 'works_from', 'works_to']


class WorkingTimeException(models.Model):
    date_start   = models.DateField(blank = False, null = False, verbose_name = 'День начала')
    date_end     = models.DateField(blank = False, null = False, verbose_name = 'День окончания')
    works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени')
    works_to    = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Конец рабочего времени')
    weekend     = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Выходной')
    is_annual   = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Ежегодно')
    description = models.CharField(max_length = 64, blank = True, null = True, verbose_name = 'Описание')
    # Set possible only to Item & Service
    content_type    = models.ForeignKey(
            ContentType, 
            on_delete = models.CASCADE, 
            limit_choices_to = 
                models.Q(app_label = 'service', model = 'service') 
                | models.Q(app_label = 'service', model = 'item'), 
            blank = False, null = False, verbose_name = 'Тип назначения'
        )
    object_id       = models.PositiveIntegerField(blank = False, null = False, verbose_name = 'Id назначения')
    # Enables to set 'content_type' and 'object_id' by assigning
    # the destination object to this field:
    service_or_item = GenericForeignKey('content_type', 'object_id')
    class Meta:
        verbose_name        = 'Дата исключения'
        verbose_name_plural = 'Даты исключений'
        ordering = ['object_id', 'is_annual', 'date_start', 'date_end', 'works_from']


class Service(models.Model):
    url_id      = models.CharField(max_length = 16, blank = False, null = False, unique = True, verbose_name = 'Фрагмент URL на английском')
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    description = models.CharField(max_length = 124, blank = False, null = False, verbose_name = 'Краткое описание')
    instruction = models.TextField(blank = True, null = True, verbose_name = 'Инструкция и подробное описание')    
    time_step   = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
    max_time_steps  = models.PositiveSmallIntegerField(blank = False, null = False, default = 1, verbose_name = 'Максимальное число шагов времени непрерывного использования')
    default_price   = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена по-умолчанию за шаг времени', default = 0)
    edited      = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование этих данных')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    default_works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени по-умолчанию')
    default_works_to    = models.TimeField(blank = False, null = False, default = datetime.time(23,59,59), verbose_name = 'Конец рабочего времени по-умолчанию')
    days_to_show        = models.PositiveSmallIntegerField(default = 3, validators = [MinValueValidator(1)], blank = False, null = False, verbose_name = 'Дней на заказ')
    time_after_now      = models.TimeField(blank = False, null = False, default = datetime.time(0,20,0), verbose_name = 'Времени на запись после начала')
    working_times       = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    responsible_user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = 'ответственное лицо')
    def __str__(self):
        return self.name
    def get_timetable_list(self):
        items = {}
        for item in list(self.items.all()):
            items[item.id] = item.get_available_time()
    def clean(self):
        if self.default_works_to < self.default_works_from:
            raise ValidationError('Please use time of single day')
    # Django doesn`t call full_clean (clean_fields, clean, validate_unique)
    # no save() by default
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Service, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'


class Item(models.Model):
    # 'id' field will be added automatically 
    name        = models.CharField(max_length = 64, unique = True, blank = False, null = False, verbose_name = 'Название/номер')
    service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    price       = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена за шаг времени', default = 0)
    location    = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Расположение')
    t_steps_per_order   = models.PositiveSmallIntegerField(default = 1, 
            validators = [MinValueValidator(1)],
            blank = False, null = False, verbose_name = 'Число шагов времени на заказ')
    extra_info  = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Доп. информация')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    created     = models.DateTimeField(auto_now_add = True, null = False, verbose_name = 'Введено в строй')
    working_times       = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    def get_working_time(self, day):
        if self.is_active == False or self.service.is_active == False:
            return {'works_from': datetime.time(0,0,0),
                    'works_to': datetime.time(0,0,0),
                    'weekend': True}
        # 2 same code -> function (requires same class fields, if used)
        def get_working_time_exception_query(source, day):
            # remember, that exceptions may be annual (weekends)
            return (source.working_time_exceptions.all().filter(
                # Remember [X, Y)
                # day & month
                models.Q(date_start__day__lte = day.day, 
                    date_end__day__gt = day.day, 
                    date_start__month__lte = day.month, 
                    date_end__month__gte = day.month) 
                # year | is_annual
                & (
                    models.Q(date_start__year__lte = day.year, 
                        date_end__year__gte = day.year) 
                    | models.Q(is_annual = True)
                )
            ))
        def get_working_time_query(source, day):
            return (source.working_times.all().filter(
                # everyday
                models.Q(weekday = WorkingTime.EVERYDAY)
                # weekday returns [0,6], but we have [1,7]
                | models.Q(weekday = day.weekday() + 1)
            ))
        # PRIORITY: Service < Item < WorkingTime < WorkingTimeException
        # working_time_exceptions
        wte_item = get_working_time_exception_query(self, day)
        if wte_item.exists():
            return {'works_from': wte_item.first().works_from,
                    'works_to': wte_item.first().works_to,
                    'weekend': wte_item.first().weekend}
        # same for service
        wte_service = get_working_time_exception_query(self.service, day)
        if wte_service.exists():
            return {'works_from': wte_service.first().works_from,
                    'works_to': wte_service.first().works_to,
                    'weekend': wte_service.first().weekend}
        # working_times
        wt_item = get_working_time_query(self, day)
        if wt_item.exists():
            return {'works_from': wt_item.first().works_from,
                    'works_to': wt_item.first().works_to,
                    'weekend': wt_item.first().weekend}
        # same for service
        wt_service = get_working_time_query(self.service, day)
        if wt_service.exists():
            return {'works_from': wt_service.first().works_from,
                    'works_to': wt_service.first().works_to,
                    'weekend': wt_service.first().weekend}
        return {'works_from': self.service.default_works_from,
                'works_to': self.service.default_works_to,
                'weekend': False}
    def get_orders(self, day):
        orders = list(self.orders.all().filter(
            models.Q(date_start = day)
            | (models.Q(date_start = day - datetime.timedelta(days = 1),
                    time_start__gt = models.F('time_end'))
                # order {23:30, 00:00}
                & ~models.Q(time_end = datetime.time(0,0,0)))
        ).order_by('time_end'))
        result_lst = [None]*len(orders)
        for i in range(len(orders)):
            result_lst[i] = {}
            if orders[i].contains_midnight():
                if orders[i].date_start != day:
                    result_lst[i]['time_start'] = datetime.time(0,0,0)
                    result_lst[i]['time_end'] = orders[i].time_end
                else:
                    result_lst[i]['time_end'] = datetime.time(0,0,0)
                    result_lst[i]['time_start'] = orders[i].time_start
            else:
                    result_lst[i]['time_start'] = orders[i].time_start
                    result_lst[i]['time_end'] = orders[i].time_end
            result_lst[i]['user'] = orders[i].user
            result_lst[i]['contains_midnight'] = orders[i].contains_midnight()
        return result_lst
    def gen_list_of_intervals(self, time_start, time_end):
        # Strange Python has timedelta only for datetime, not time
        td = datetime.datetime.combine(datetime.date.min, 
            self.service.time_step) - datetime.datetime.min
        td *= self.t_steps_per_order
        t_end = datetime.datetime.combine(datetime.date.min, time_start) + td
        te = datetime.datetime.combine(datetime.date.min, time_end)
        if te.time() == datetime.time(0,0,0):
            te += datetime.timedelta(days = 1)
        result_lst = []
        while t_end <= te:
            result_lst.append(
                    {'time_start': (t_end - td).time(), 'time_end': t_end.time()}
            )
            t_end += td
        return result_lst
    def get_available_time(self):
        def erase_from_order(in_lst, order):
            for l in in_lst:
                if (
                    l['time_start'] <= order['time_start']
                    and (order['time_start'] <= l['time_end']
                        or l['time_end'] == datetime.time(0,0,0))
                ):
                    #print(1)
                    #print(order['time_start'])
                    l['user'] = order['user']
                elif (
                    # Remember [X, Y)
                    l['time_start'] < order['time_end']
                    and ((order['time_end'] <= l['time_end']
                        and order['time_end'] != datetime.time(0,0,0))
                    or (l['time_end'] == datetime.time(0,0,0)
                        and order['time_end'] != datetime.time(0,0,0)))
                ):
                    #print(2)
                    #print(order['time_start'])
                    l['user'] = order['user']
                elif (
                    order['time_start'] <= l['time_start']
                    and ((l['time_end'] <= order['time_end']
                            and l['time_end'] != datetime.time(0,0,0))
                        or order['time_end'] == datetime.time(0,0,0))
                ):
                    #print(3)
                    #print(order['time_start'])
                    l['user'] = order['user']

        orders = self.orders.all()
        result_time_list = []
        dtime = datetime.datetime.now()
        today = datetime.date.today()
        for i in range(self.service.days_to_show):
            day = today + datetime.timedelta(days = i)
            from_to_or_weekend = self.get_working_time(day)
            if from_to_or_weekend['weekend'] == True:
                result_time_list[i] = []
            else:
                lst = self.gen_list_of_intervals(
                        from_to_or_weekend['works_from'], 
                        from_to_or_weekend['works_to']
                )
                orders = self.get_orders(day)
                for o in orders:
                    erase_from_order(lst, o)
                result_time_list.append(lst)
        return result_time_list
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'предмет сервиса'
        verbose_name_plural = 'предметы сервиса'
        ordering = ['location', 'price']


class Order(models.Model):
    date_start  = models.DateField(default = datetime.date.today(), blank = False, null = False, verbose_name = 'Дата')
    time_start  = models.TimeField(blank = False, null = False, unique = True, verbose_name = 'Время начала')
    time_end    = models.TimeField(blank = False, null = False, unique = True, verbose_name = 'Время конца')
    item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    # time_start > time_end is normal, we say it means 'finish next day'
    def contains_midnight(self):
        return self.time_start > self.time_end and self.time_end != datetime.time(0,0,0)
    # Validation
    def clean(self):
        if self.date_start < datetime.date.today():
            raise ValidationError('date_start can`t be before today()')
        order_lst = list(Order.objects.all().filter(
            models.Q(date_start = self.date_start)
            | (models.Q(date_start = self.date_start 
                    - datetime.timedelta(days = 1),
                time_start__gt = models.F('time_end'))
                # order {23:30, 00:00}
                & ~models.Q(time_end = datetime.time(0,0,0)))
        ).order_by('time_end'))
        for o in order_lst:
            if (
                o.time_start <= self.time_start
                and (self.time_start <= o.time_end
                    or o.time_end == datetime.time(0,0,0))
            ):
                raise ValidationError('Order is in conflict with the order [{0}-{1})'.format(o.time_start, o.time_end))
            elif (
                # Remember [X, Y)
                o.time_start < self.time_end
                and ((self.time_end <= o.time_end
                    and self.time_end != datetime.time(0,0,0))
                or (o.time_end == datetime.time(0,0,0)
                    and self.time_end != datetime.time(0,0,0)))
            ):
                raise ValidationError('Order is in conflict with the order [{0}-{1})'.format(o.time_start, o.time_end))
            elif (
                self.time_start <= o.time_start
                and ((o.time_end <= self.time_end
                        and o.time_end != datetime.time(0,0,0))
                    or self.time_end == datetime.time(0,0,0))
                and (True if self.contains_midnight() 
                    and o.contains_midnight() else False)
            ):
                raise ValidationError('Order is in conflict with the order [{0}-{1})'.format(o.time_start, o.time_end))

    # Django doesn`t call full_clean (clean_fields, clean, validate_unique)
    # no save() by default
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Order, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

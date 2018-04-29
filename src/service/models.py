# coding: utf-8
# NOTE: all times use the pattern [X, Y)
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone
from precise_bbcode.fields import BBCodeTextField
from math import gcd
import datetime
import types

from .timetable import Timetable, TimetableList, OrderedInterval

from utils.model_aliases import DefaultImageField

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
    works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени (включительно)')
    works_to    = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Конец рабочего времени (не включительно)')
    is_weekend     = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Выходной')
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
    date_start   = models.DateField(default = datetime.date.today, blank = False, null = False, verbose_name = 'День начала (включительно)')
    date_end     = models.DateField(default = datetime.date.today, blank = False, null = False, verbose_name = 'День окончания (включительно)')
    works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени (включительно)')
    works_to    = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Конец рабочего времени (не включительно)')
    is_weekend     = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Выходной')
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


def get_working_time_exception_query(source, day):
    # remember, that exceptions may be annual (weekends)
    return (source.working_time_exceptions.all().filter(
        # Remember [X, Y)
        # day & month
        models.Q(date_start__day__lte = day.day, 
            date_end__day__gte = day.day, 
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
        # weekday() returns [0,6], but we have [1,7]
        | models.Q(weekday = day.weekday() + 1)
    ))


class Service(models.Model):
    # URL part. Django accepts only exactly 'slug' field in urls.py
    slug        = models.SlugField(max_length = 16, blank = False, null = False, unique = True, verbose_name = 'Фрагмент URL на английском (навсегда)')
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    announcements = BBCodeTextField(blank = True, null = True, verbose_name = 'Объявления')
    instruction = BBCodeTextField(blank = True, null = True, verbose_name = 'Инструкция и подробное описание')    
    image       = DefaultImageField(blank = False, null = False)
    timestep    = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
    max_time_steps  = models.PositiveSmallIntegerField(blank = False, null = False, default = 1, verbose_name = 'Максимальное число шагов времени непрерывного использования')
    default_price   = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена по-умолчанию за шаг времени', default = 0)
    edited      = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование этих данных')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    default_works_from  = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Начало рабочего времени по-умолчанию')
    default_works_to    = models.TimeField(blank = False, null = False, default = datetime.time(00,00,00), verbose_name = 'Конец рабочего времени по-умолчанию')
    days_to_show        = models.PositiveSmallIntegerField(default = 3, validators = [MinValueValidator(1)], blank = False, null = False, verbose_name = 'Дней на заказ')
    time_after_now      = models.TimeField(blank = False, null = False, default = datetime.time(0,20,0), verbose_name = 'Времени на запись после начала')
    working_times       = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    responsible_user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = 'Ответственное лицо')
    responsible_room    = models.CharField(max_length = 32, blank = True, null = True, verbose_name = 'Комната ответственного')
    request_document        = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf', 'odt', 'png', 'jpg', 'jpeg'])], blank = True, null = True, verbose_name = 'Служебка (doc/docx/pdf/odt/png/jpg/jpeg)')
    is_single_item      = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Один предмет сервиса')
    is_finished_hidden  = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Скрывать прошедшие интервалы')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def get_absolute_url(self):
        return reverse('service:service', args=[self.slug])
    def __str__(self):
        return self.name
    # Return { 'works_from', 'works_to', 'is_weekend', 'is_exception' }
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
            return {'works_from': exception.works_from,
                    'works_to': exception.works_to,
                    'is_weekend': exception.is_weekend,
                    'is_exception': True}
        # working_time
        wt_service = get_working_time_query(self, day)
        if wt_service.exists():
            working_time = wt_service.first()
            return {'works_from': working_time.works_from,
                    'works_to': working_time.works_to,
                    'is_weekend': working_time.is_weekend,
                    'is_exception': False}
        # default
        return {'works_from': self.default_works_from,
                'works_to': self.default_works_to,
                'is_weekend': False,
                'is_exception': False}
    # Return {'date','datestr',
    #   'is_weekend': bool,
    #   'items': {'name': {
    #                       'is_open','price','rowspan',
    #                       'time':[TimetableInterval]
    #                     }
    #            }
    #   'timetable': [TimetableInterval]
    # }
    # or None if not working
    def get_timetable(self, date):
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
        service_timetable.set_date(date)
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
        if self.is_finished_hidden and date == timezone.now().date():
            timetables.crop_time_start(timezone.now(), leave_closed_cells_num = 1)
        final_timetables = timetables.get_timetables()
        result = {'date': s, 'is_weekend': False, 'items': {}}
        # Database needs to order properly
        for it in list(self.items.all()):
            t = final_timetables[it.name]
            lst = t.gen_head()
            lst.extend(t.gen_list())
            lst.extend(t.gen_tail())
            result['items'][it.name] = {'is_open': t.is_open, 'price': it.get_price(), 'rowspan': t.timesteps_per_order, 'time': lst}
        lst = final_timetables[''].gen_head()
        lst.extend(final_timetables[''].gen_list())
        lst.extend(final_timetables[''].gen_tail())
        result['timetable'] = lst
        return result
    # Return [{'date','datestr',
    #   'is_weekend': bool,
    #   'items': {'name': ...}
    # }]
    # or None if not working
    def gen_timetable_layout(self):
        # is_active is immediate
        if not self.is_active:
            return None
        result = []
        now = timezone.now().date()
        for i in range(self.days_to_show):
            result.append(self.get_timetable(now + datetime.timedelta(days = i)))
        return result
    def get_timetable_list(self):
        # cleans trailing 'closed' marks
        def clean_starting(time_lst):
            # Flag to 'break' double loop
            clean_flag = True
            index = 0
            result = {}
            while clean_flag == True:
                for it in time_lst.values():
                    if (it['time'] and 'closed' not in it['time'][index]
                        and 'weekend' not in it['time'][index]):
                        clean_flag = False
                        if index == 0:
                            result['time_start'] = it['time'][0]['time_start']
                        else:
                            result['time_end'] = it['time'][-1]['time_end']
                if clean_flag == True:
                    for it in time_lst.values():
                        del it['time'][index]
                else:
                    if index == 0:
                        # in Python [-1] returns last element
                        index = -1
                        clean_flag = True
                    else:
                        return result
        def get_closed_for_gdc(lst, result_lst):
            num = 0
            for l in lst:
                if 'closed' in l:
                    num += 1
                elif num != 0:
                    result_lst.append(types.SimpleNamespace(t_steps_per_order = num))
                    num = 0
            if num != 0:
                result_lst.append(types.SimpleNamespace(t_steps_per_order = num))
        def final_prepare_first_day(final_lst, latest_time):
            # Removes leading passed cells
            # 'latest_time' is used in 'weekend' case
            if not final_lst or not final_lst[0]['items']:
                return
            # First day
            lst = final_lst[0]
            earliest_time = None
            now = timezone.now().time()
            # Weekends have no 'time_start' or 'time_end'
            weekend_lst = []
            # Find the earliest time
            for it in list(lst['items'].values()):
                if it['time'] and 'weekend' not in it['time'][0]:
                    t_list = it['time']
                    for t in t_list:
                        if ((t['time_end'] > now 
                                or t['time_end'] == datetime.time(0,0,0)) 
                            and (earliest_time == None 
                                or earliest_time > t['time_start'])):
                            earliest_time = t['time_start']
                            break
                    if not earliest_time:
                        earliest_time = datetime.time(23, 59, 59)
            # Remove all before 'earliest'
            for i in range(len(lst['time_layout'])):
                if lst['time_layout'][i]['time_start'] >= earliest_time:
                    lst['time_layout'] = lst['time_layout'][i:]
                    break
            td = (datetime.datetime.combine(datetime.date.min, self.time_step) - datetime.datetime.min)
            # Fill [earliest, next time_start] 
            # with 'closed' cells with duration=1
            for k in lst['items']:
                t = lst['items'][k]['time']
                # Empty case
                if not t:
                    t_start = datetime.datetime.combine(datetime.date.min, earliest_time)
                    while t_start < datetime.datetime.combine(datetime.datetime.min, latest_time):
                        t.append({'time_start': t_start.time(), 'time_end': (t_start + td).time(), 'closed': True})
                        t_start += td
                elif 'weekend' not in t[0]:
                    for i in range(len(t)):
                        if t[i]['time_start'] >= earliest_time:
                            t = t[i:]
                            t_start = datetime.datetime.combine(datetime.date.min, t[0]['time_start'])
                            while (t_start >= datetime.datetime.min + td
                                    and (t_start - td).time() >= earliest_time):
                                t.insert(0, {'time_start': (t_start - td).time(), 'time_end': t[0]['time_start'], 'closed': True})
                                t_start = datetime.datetime.combine(datetime.date.min, t[0]['time_start'])
                            break
                    lst['items'][k]['time'] = t
                else:
                    # A big single cell
                    lst['items'][k]['time'] = [{'weekend': True, 'time_start': earliest_time, 'time_end': latest_time}]
        # collect available_time from all Items
        items = {}
        for item in list(self.items.all().order_by('name')):
            items[item.name] = item.get_available_time()
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        # timedelta is available for datetime only
        now = timezone.now()
        # To be used in final_prepare_first_day
        latest_time_first_day = None
        # start generating result
        result_lst = []
        for i in range(self.days_to_show):
            result_lst.append({
                'day': '{0} {1}'.format(weekdays[(now + datetime.timedelta(days = i)).date().weekday()], (now + datetime.timedelta(days = i)).strftime('%d.%m')),
                'dateyear': str((now + datetime.timedelta(days = i)).date()),
                'items': {},
                'time_layout': []
            })
            # This is used twice:
            # First: item names to create time layout
            # Second: time layout
            tmp_lst = []
            for name, value in items.items():
                result_lst[i]['items'][name] = {}
                result_lst[i]['items'][name]['time'] = items[name][i]
                # If not set, 'weekend' case will not be set
                result_lst[i]['items'][name]['rowspan'] = 1
                if 'weekend' not in items[name][i][0].keys():
                    tmp_lst.append(name)
            if not tmp_lst:
                result_lst[i]['global_weekend'] = True
            else:
                # get gcd to make cells smaller if all of them are big
                tmp_lst = list(self.items.all().filter(name__in = tmp_lst))
                for m in result_lst[i]['items'].values():
                    get_closed_for_gdc(m['time'], tmp_lst)
                res = tmp_lst[0].t_steps_per_order
                for c in tmp_lst[1:]:
                    res = gcd(res, c.t_steps_per_order)
                for it in tmp_lst:
                    # we have poisoned tmp_lst in get_closed_for_gcd
                    if hasattr(it, 'name'):
                        result_lst[i]['items'][it.name]['rowspan'] = int(it.t_steps_per_order / res)
                # erase trailing 'closed'
                time_start_end = clean_starting(result_lst[i]['items'])
                # generate time_layout
                td = (datetime.datetime.combine(datetime.date.min, self.time_step) - datetime.datetime.min)*res
                t_start = datetime.datetime.combine(datetime.date.min, time_start_end['time_start'])
                t_end = datetime.datetime.combine(datetime.date.min, time_start_end['time_end'])
                if t_end.time() == datetime.time(0,0,0):
                    t_end += datetime.timedelta(days = 1)
                tmp_lst = []
                while t_start + td <= t_end:
                    tmp_lst.append({
                        'time_start': t_start.time(),
                        'time_end': (t_start + td).time()
                    })
                    t_start += td
                result_lst[i]['time_layout'] = tmp_lst
                if i == 0:
                    # latest in layout
                    latest_time_first_day = tmp_lst[-1]['time_end']
        # Make first day smaller
        if 'global_weekend' not in result_lst[0]:
            final_prepare_first_day(result_lst, latest_time_first_day)
        return result_lst
    # Return [{}]
    # Return {item_name: {price, timesteps_per_order}}
    def get_item_info(self):
        result = {}
        for it in self.items.all():
            result[it.name] = {
                    'price': it.get_price(),
                    'timesteps_per_order': self.t_steps_per_order
                }
        return result_lst
    def clean(self):
        #if self.default_works_to < self.default_works_from:
        #    raise ValidationError('Please, set working times in 1 day')
        if self.is_single_item and self.items.count() != 1:
            raise ValidationError('If is_single_item is set, their count must be = 1 too')
    # Django doesn`t call full_clean (clean_fields, clean, validate_unique)
    # no save() by default
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Service, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'
        ordering            = ['order']


class Item(models.Model):
    # 'id' field will be added automatically 
    name        = models.CharField(max_length = 64, unique = True, blank = False, null = False, verbose_name = 'Название/номер')
    service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    price       = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена за шаг времени', default = None)
    location    = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Расположение')
    t_steps_per_order   = models.PositiveSmallIntegerField(default = 1, 
            validators = [MinValueValidator(1)],
            blank = False, null = False, verbose_name = 'Число шагов времени на заказ')
    extra_info  = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Доп. информация')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    created     = models.DateTimeField(auto_now_add = True, null = False, verbose_name = 'Введено в строй')
    working_times       = GenericRelation(WorkingTime, content_type_field = 'content_type', object_id_field = 'object_id')
    working_time_exceptions = GenericRelation(WorkingTimeException, content_type_field = 'content_type', object_id_field = 'object_id')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    # Return { 'works_from', 'works_to', 'is_weekend', 'is_exception' }
    # or None if not working
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
            return {'works_from': exception.works_from,
                    'works_to': exception.works_to,
                    'is_weekend': exception.weekend,
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
            return {'works_from': working_time.works_from,
                    'works_to': working_time.works_to,
                    'is_weekend': working_time.is_weekend,
                    'is_exception': False}
        # if no special for item, return service results
        return service_working_time
    # Return { 'date':         str(%d.%m),
    #          'price':        int,
    #          'is_weekend':   bool,
    #          'timetable':    Timetable(start=first, end=last)
    #          'is_exception': bool }
    # or None if not working
    def get_timetable(self, date):
        # is_active is immediate
        if not self.is_active:
            return None
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        working_time = self.get_working_time(date)
        s = '{0} {1}'.format(weekdays[date.weekday()], date.strftime('%d.%m'))
        #print('# Item start')
        #print(str(working_time))
        if not working_time or working_time['is_weekend']:
            return {'date': s, 'price': self.get_price(), 
                    'is_weekend': True, 'timetable': None, 
                    'is_exception': True}
        else:
            timetable = Timetable(
                timestep = self.service.timestep,
                start = working_time['works_from'], 
                end = working_time['works_to'],
                first = working_time['works_from'], 
                last = working_time['works_to'],
                timesteps_per_order = self.t_steps_per_order)
            timetable.set_date(date)
            raw_orders = list(self.orders.all().filter(is_approved = True).filter(models.Q(date_start = date) | models.Q(date_start = date - datetime.timedelta(days = 1)) | models.Q(date_start = date + datetime.timedelta(days = 1))))
            timetable.add_ordered(raw_orders, 
                    lambda o: OrderedInterval(
                        start = datetime.datetime.combine(o.date_start,
                            o.time_start),
                        end = datetime.datetime.combine(o.date_start,
                            o.time_end) + datetime.timedelta(days = 1 if o.time_start > o.time_end else 0),
                        nid = o.pk,
                        extra_data = {'user': o.user,
                            'participations': list(o.participations.all()),
                            'title': o.title}
                    )
                )
            #print('# Item end')
            return {'date': s, 'price': self.get_price(), 
                    'is_weekend': False, 'timetable': timetable,
                    'is_exception': working_time['is_exception']}
    def get_price(self):
        return self.price if self.price != None else self.service.default_price
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Item, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'предмет сервиса'
        verbose_name_plural = 'предметы сервиса'
        ordering = ['order', 'location', 'price']


class Order(models.Model):
    date_start  = models.DateField(default = datetime.date.today, blank = False, null = False, verbose_name = 'Дата')
    time_start  = models.TimeField(blank = False, null = False, verbose_name = 'Время начала')
    time_end    = models.TimeField(blank = False, null = False, verbose_name = 'Время конца')
    item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    title       = models.TextField(blank = True, null = True, verbose_name = 'Назначение заказа')
    is_approved = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Одобрено')
    payed       = models.PositiveSmallIntegerField(blank = False, null = False, verbose_name = 'Оплачено')
    # time_start > time_end is normal, we say it means 'finish next day'
    def contains_midnight(self):
        return self.time_start > self.time_end and self.time_end != datetime.time(0,0,0)
    # Validation
    def clean(self):
        if self.date_start < datetime.date.today():
            raise ValidationError('date_start can`t be before today()')
        order_lst = list(Order.objects.all().filter(
            (
                models.Q(date_start = self.date_start)
                | (models.Q(date_start = self.date_start 
                        - datetime.timedelta(days = 1),
                    time_start__gt = models.F('time_end'))
                    # order {23:30, 00:00}
                    & ~models.Q(time_end = datetime.time(0,0,0)))
            ) & ~models.Q(pk = self.pk) & models.Q(item = self.item)
            & models.Q(is_approved = True)
        ).order_by('time_end'))
        for o in order_lst:
            if (
                # Remember [X, Y)
                o.time_start <= self.time_start
                and (self.time_start < o.time_end
                    or o.time_end == datetime.time(0,0,0))
            ):
                raise ValidationError('Order [{0}-{1}] is in conflict with the order [{2}-{3}]'.format(self.time_start, self.time_end, o.time_start, o.time_end))
            elif (
                # Remember [X, Y)
                o.time_start < self.time_end
                and ((self.time_end <= o.time_end
                    and self.time_end != datetime.time(0,0,0))
                or (o.time_end == datetime.time(0,0,0)
                    and self.time_end != datetime.time(0,0,0)))
            ):
                raise ValidationError('Order [{0}-{1}] is in conflict with the order [{2}-{3})'.format(self.time_start, self.time_end, o.time_start, o.time_end))
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
        self.clean()
        return super(Order, self).save(*args, **kwargs)
    def __str__(self):
        return '{0} ({1} {2}-{3})'.format(self.item.name, self.date_start.strftime('%Y-%m-%d'), self.time_start.strftime('%H:%M:%S'), self.time_end.strftime('%H:%M:%S'))
    def __repr__(self):
        return self.__str__()
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['is_approved', '-date_start', 'time_start']

class Participation(models.Model):
    order   = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = 'participations', blank = False, null = False, verbose_name = 'Событие')
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'participations', blank = False, null = False, verbose_name = 'Пользователь')
    def clean(self):
        if self.user.participations.filter(order = self.order).exists():
            raise ValidationError('Participation already exists!')
    def save(self, *args, **kwargs):
        self.clean()
        return super(Participation, self).save(*args, **kwargs)
    class Meta:
        verbose_name = 'Участие'
        verbose_name_plural = 'Участия'
        ordering = ['-order', 'user']

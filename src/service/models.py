# coding: utf-8
# NOTE: all times use the pattern [X, Y)
from django.db import models
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
    works_to    = models.TimeField(blank = False, null = False, default = datetime.time(0,0,0), verbose_name = 'Конец рабочего времени')
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


class Service(models.Model):
    # URL part. Django accepts only exactly 'slug' field in urls.py
    slug        = models.SlugField(max_length = 16, blank = False, null = False, unique = True, verbose_name = 'Фрагмент URL на английском (навсегда)')
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    description = models.CharField(max_length = 124, blank = False, null = False, verbose_name = 'Краткое описание')
    instruction = BBCodeTextField(blank = True, null = True, verbose_name = 'Инструкция и подробное описание')    
    image       = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'svg'])], blank = False, null = False, verbose_name = 'Картинка')
    time_step   = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
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
    request_document        = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf', 'odt', 'png', 'jpg', 'jpeg'])], blank = True, null = True, verbose_name = 'Служебка (doc/docx/pdf/odt/png/jpg/jpeg)')
    is_single_item      = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Один предмет сервиса')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def __str__(self):
        return self.name
    def get_timetable_list(self):
        # cleans trailing 'closed' marks
        def clean_starting(time_lst):
            clean_flag = True
            index = 0
            result = {}
            while clean_flag == True:
                for it in time_lst.values():
                    if 'closed' not in it['time'][index]:
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
        # collect available_time from all Items
        items = {}
        for item in list(self.items.all().order_by('name')):
            items[item.name] = item.get_available_time()
        weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        # timedelta is available for datetime only
        now = timezone.now()
        # start generating result
        result_lst = []
        for i in range(self.days_to_show):
            result_lst.append({
                'day': '{0} {1}'.format(weekdays[(now + datetime.timedelta(days = i)).date().weekday()], (now + datetime.timedelta(days = i)).strftime('%d.%m')),
                'dateyear': str((now + datetime.timedelta(days = i)).date()),
                'items': {},
                'time_layout': []
            })
            # time layout
            tmp_lst = []
            for name, value in items.items():
                result_lst[i]['items'][name] = {}
                result_lst[i]['items'][name]['time'] = items[name][i]
                if 'weekend' not in items[name][i][0].keys():
                    tmp_lst.append(name)
            if not tmp_lst:
                result_lst[i]['time_layout'] = [{'time_start': 'Отгул', 'time_end': 'Отгул'}]
                for it in result_lst[i]['items']:
                    it['rowspan'] = int(1)
            else:
                # get gcd
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
        return result_lst
    def get_item_info(self):
        result_lst = {'price':{}, 'timestep':{}}
        for it in self.items.all():
            td = datetime.datetime.combine(datetime.date.min, 
                self.time_step) - datetime.datetime.min
            td *= it.t_steps_per_order
            timestep = (datetime.datetime.min + td).time()
            if it.price:
                result_lst['price'][it.name] = it.price
                result_lst['timestep'][it.name] = timestep
            else:
                result_lst['price'][it.name] = self.default_price
                result_lst['timestep'][it.name] = timestep
        return result_lst
    def clean(self):
        if self.default_works_to < self.default_works_from:
            raise ValidationError('Please use time of single day')
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
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def _add_user_by_order(in_lst, order):
        for l in in_lst:
            if (
                l['time_start'] <= order['time_start']
                and (order['time_start'] < l['time_end']
                    or l['time_end'] == datetime.time(0,0,0))
            ):
                #print(1)
                #print(order['time_start'])
                if 'user' in order:
                    l['user'] = order['user']
                if 'title' in order:
                    l['title'] = order['title']
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
                if 'user' in order:
                    l['user'] = order['user']
                if 'title' in order:
                    l['title'] = order['title']
            elif (
                order['time_start'] <= l['time_start']
                and ((l['time_end'] <= order['time_end']
                        and l['time_end'] != datetime.time(0,0,0))
                    or order['time_end'] == datetime.time(0,0,0))
            ):
                #print(3)
                #print(order['time_start'])
                if 'user' in order:
                    l['user'] = order['user']
                if 'title' in order:
                    l['title'] = order['title']
    def get_working_time(self, day):
        if self.is_active == False or self.service.is_active == False:
            return {'works_from': datetime.time(0,0,0),
                    'works_to': datetime.time(0,0,0),
                    'weekend': True}
        # PRIORITY: Service < Item < WorkingTime < WorkingTimeException
        # working_time_exceptions
        item_result = service_result = {}
        wte_item = get_working_time_exception_query(self, day)
        if wte_item.exists():
            item_result = wte_item.first()
        # same for service
        wte_service = get_working_time_exception_query(self.service, day)
        if wte_service.exists():
            service_result = wte_service.first()
        # working_times
        wt_item = get_working_time_query(self, day)
        if wt_item.exists() and not item_result:
            item_result = wt_item.first()
        # same for service
        wt_service = get_working_time_query(self.service, day)
        if wt_service.exists() and not servise_result:
            service_result = wt_service.first()
        if not service_result:
            service_result = {
                'works_from': self.service.default_works_from,
                'works_to': self.service.default_works_to,
                'weekend': False
            }
        else:
            service_result = {
                'works_from': service_result.works_from,
                'works_to': service_result.works_to,
                'weekend': service_result.weekend
            }
        if not item_result:
            item_result = service_result
        else:
            item_result = {
                'works_from': item_result.works_from,
                'works_to': item_result.works_to,
                'weekend': item_result.weekend
            }
        td = datetime.datetime.combine(datetime.date.min, 
            self.service.time_step) - datetime.datetime.min
        # service time start/end
        sts = datetime.datetime.combine(datetime.date.min, 
            service_result['works_from'])
        ste = datetime.datetime.combine(datetime.date.min, 
            service_result['works_to'])
        if ste.time() == datetime.time(0,0,0):
            ste += datetime.timedelta(days = 1)
        to_prepend = []
        to_append = []
        t_start = datetime.datetime.combine(datetime.date.min, item_result['works_from'])
        t_end = datetime.datetime.combine(datetime.date.min, item_result['works_to'])
        if not item_result['weekend']:
            if t_start < sts:
                t_start = sts
            elif t_start > sts:
                while t_start > sts:
                    to_prepend.append(
                            {'time_start': sts.time(), 'time_end': (sts + td).time(), 'closed': True}
                    )
                    sts += td
                t_start = sts
            t_end = sts + (
                ((datetime.datetime.combine(datetime.date.min, self.service.time_step) - datetime.datetime.min)*self.t_steps_per_order) 
                * ((ste - sts) 
                    // ((datetime.datetime.combine(datetime.date.min, self.service.time_step) - datetime.datetime.min)*self.t_steps_per_order))
            )
            if t_end > ste and ste.time() != datetime.time(0,0,0) or t_end.time() == datetime.time(0,0,0):
                t_end = ste
            elif t_end < ste:
                while t_end < ste:
                    to_append.insert(0, 
                            {'time_start': (ste - td).time(), 'time_end': ste.time(), 'closed': True}
                    )
                    ste -= td
                t_end = ste
        orders = self.get_orders(day)
        for o in orders:
            Item._add_user_by_order(to_prepend, o)
            Item._add_user_by_order(to_append, o)
        return {
            'works_from': t_start.time(),
            'works_to': t_end.time(),
            'weekend': item_result['weekend'],
            'to_prepend': to_prepend,
            'to_append': to_append
        }
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
            if orders[i].approved:
                result_lst[i]['user'] = orders[i].user
            if orders[i].title:
                result_lst[i]['title'] = orders[i].title
            result_lst[i]['contains_midnight'] = orders[i].contains_midnight()
        return result_lst
    def gen_list_of_intervals(self, time_start, time_end):
        # Python has timedelta only for datetime, not time
        td = datetime.datetime.combine(datetime.date.min, 
            self.service.time_step) - datetime.datetime.min
        td *= self.t_steps_per_order
        t_start = datetime.datetime.combine(datetime.date.min, time_start)
        t_end = datetime.datetime.combine(datetime.date.min, time_end)
        if t_end.time() == datetime.time(0,0,0):
            t_end += datetime.timedelta(days = 1)
        result_lst = []
        while t_start + td <= t_end:
            result_lst.append(
                    {'time_start': t_start.time(), 'time_end': (t_start + td).time()}
            )
            t_start += td
        return result_lst
    def get_available_time(self):

        result_time_list = []
        dtime = timezone.now()
        today = datetime.date.today()
        for i in range(self.service.days_to_show):
            day = today + datetime.timedelta(days = i)
            time_sources = self.get_working_time(day)
            if time_sources['weekend'] == True:
                result_time_list[i] = [{'weekend': True}]
            else:
                lst = self.gen_list_of_intervals(
                        time_sources['works_from'], 
                        time_sources['works_to']
                )
                orders = self.get_orders(day)
                for o in orders:
                    Item._add_user_by_order(lst, o)
                #print('{0}:\n   {1}\n   {2}\n    {3}'.format(self.name, str(lst), str(time_sources['to_prepend']), str(time_sources['to_append'])))
                lst[:0] = time_sources['to_prepend']
                lst.extend(time_sources['to_append'])
                result_time_list.append(lst)
        return result_time_list
    def get_price(self):
        return self.price if self.price else self.service.default_price
    def __str__(self):
        return self.name
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
    approved    = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Одобрено')
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
            & models.Q(approved = True)
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
        ordering = ['-approved', '-date_start', 'time_start']
        unique_together = (('date_start', 'time_start', 'item'), ('date_start', 'time_end', 'item'),)

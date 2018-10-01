from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

import datetime

from ..utils import to_dt

# Return database filter to ServiceAbstract

def get_children_for_service_item():
    pass

# Create your models here.

class OrderItemAbstract(models.Model):
    # (date_start, time_start, time_end) make orders > 24h impossible
    # (time_start == time_end) = 24h
    date_start  = models.DateField(default = datetime.date.today, blank = False, null = False, verbose_name = 'Дата')
    time_start  = models.TimeField(blank = False, null = False, verbose_name = 'Время начала')
    time_end    = models.TimeField(blank = False, null = False, verbose_name = 'Время конца')
    # define your own 'item' field with related_name = 'orders'!
    # example:
    # item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    item        = None
    # define your own 'user' field with non-clashing related_name!
    # example:
    # user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    user        = None
    used        = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Потрачено')
    @staticmethod
    def filter_queryset(queryset):
        return queryset
    @classmethod
    def get_queryset(this_class, dt_start, dt_end, 
            td_margin_before = datetime.timedelta(), 
            td_margin_after = datetime.timedelta()):
        # Remember [X, Y)
        # Situations:
        #
        # 1 (date_start in (start.date(), end.date()) - possible!!)
        #
        # . . . . . . [order_start . order_end] . . . . .
        # . . . . . . + + + + + + + + + + + + + . . . . .
        # . . [start . . . . . . . . . . . . . . end] . .
        #
        # 2.1 (date_start == start.date())
        #
        # . . [order_start . order_end] . . . . . . . . .
        # . . + + + + + + + + + + + + + . . . . . . . . .
        # . . [start . . . . . . . . . . . . . . end] . .
        #
        # 2.2 (date_start == end.date())
        #
        # . . . . . . . . [order_start . order_end] . . .
        # . . . . . . . . + + . . . . . . . . . . . . . .
        # . . [start . . end] . . . . . . . . . . . . . .
        #
        # 3.1 (date_start == start.date() && time_start < start.time())
        #
        # . . [order_start . order_end] . . . . . . . . .
        # . . . . . . . + + + + + + + + . . . . . . . . .
        # . . . . . . . [start . . . . . . . end] . . . .
        #
        # 3.2 (date_start == start.date() - 1 && time_start >= time_end)
        #
        # . . [order_start . order_end] . . . . . . . .
        # . . . . . . . . . . . . . + + . . . . . . . .
        # . . . . . . . . . . . . . [start . . end] . .
        #

        # If td_margin_after - may be late
        start = dt_start - td_margin_after
        # If td_margin_before - may be early
        end = dt_end + td_margin_before
        day_delta = datetime.timedelta(days = 1)
        qs = this_class.objects.all().filter(
                # date_start in (start, end)
                # [possible for big td_margin_(start)/(end)]
                models.Q(date_start__gt = start.date(), date_start__lt = end.date())
                # {date_start, time_start} in [start, end)
                | (
                    models.Q(date_start = start.date(), time_start__gte = start.time()) 
                    & (
                        # Avoid
                        # . . . . . . . .[order_start . order_end].
                        # .[start . end]. . . . . . . . . . . . . .
                        models.Q(date_start__lt = end.date())
                        |
                        models.Q(date_start = end.date(), time_start__lt = end.time())
                    )
                )
                # most exotic:
                # [order_start . order_end] . . . . . . . 
                #  . . . . . . . [start . . . . . . . end]
                | models.Q(date_start = start.date(), time_start__lt = start.time(), time_end__gt = start.time())
                # same as prev., but when 'time_end' is on next date
                | models.Q(date_start = start.date(), time_start__lt = start.time(), time_start__gte = models.F('time_end'))
                # 3.2, when 1 day is not enough, the only hope: 
                # time_start <= time_end & time_end > start.time()
                | models.Q(date_start = (start - day_delta).date(), time_start__gte = models.F('time_end'), time_end__gt = start.time())
            ).distinct()
        return this_class.filter_queryset(qs)
    # time_start > time_end is normal, we say it means 'finish next day'
    def contains_midnight(self):
        return self.time_start > self.time_end and self.time_end != datetime.time(0,0,0)
    # Validate no orders overflow each other
    def clean_time_limits(self):
        [start, end] = to_dt(self.date_start, self.time_start, self.time_end).values()
        orders = self.get_queryset(start, end).filter(~models.Q(pk = self.pk), item = self.item)
        if orders.exists():
            exception_text = 'Order [{0}-{1}{2}) is in conflict with'.format(start, end, ', {}'.format(self.pk) if hasattr(self,'pk') else '')
            for o in orders:
                [start, end] = to_dt(o.date_start, o.time_start, o.time_end).values()
                exception_text += '\n    [{0}-{1}, {2})'.format(start, end, o.pk)
            raise ValidationError(exception_text)
    def clean_user_orders_max(self):
        dt = to_dt(self.date_start, self.time_start, self.time_end);
        date = self.date_start
        wt = self.item.get_working_time(date)
        if not wt:
            raise ValidationError('Item {0} not working now! (order {1})'.format(self.item, self))
        if datetime.datetime.combine(date, self.time_start) < wt['works_from']:
           date -= datetime.timedelta(days = 1)
        max_orders = self.item.service.max_continuous_orders
        timetable = self.item.get_timetable(date)
        if not timetable['timetable']:
            raise ValidationError('Can`t get timetable for order({0}) for date({1})'.format(self, date))
        else:
            timetable = timetable['timetable']
        # Gen layout with blocked intervals based on max_orders
        layout = timetable.gen_list_limited(max_orders, 'user', self.user)
        oi = -1
        # Brute search
        for l in layout:
            oi += 1
            if l.start == dt['start'] and l.end == dt['end']:
                break
        if oi == -1:
            raise ValidationError('No interval for validation found!')
        if not layout[oi].is_open:
            raise ValidationError('Can`t save order({0}) (note: the limit is ({1})'.format(self, max_orders))
    # Validation final
    def clean(self):
        if self.date_start < datetime.date.today():
            raise ValidationError('date_start can`t be before today()')
        self.clean_time_limits()
        self.clean_user_orders_max()
    # Django doesn`t call full_clean (clean_fields, clean, validate_unique)
    # no save() by default
    def save(self, *args, **kwargs):
        self.clean()
        return super(OrderItemAbstract, self).save(*args, **kwargs)
    def __str__(self):
        return '{0} ({1} {2}-{3})'.format(self.item.name, self.date_start.strftime('%Y-%m-%d'), self.time_start.strftime('%H:%M:%S'), self.time_end.strftime('%H:%M:%S'))
    def __repr__(self):
        return self.__str__()
    class Meta:
        abstract = True


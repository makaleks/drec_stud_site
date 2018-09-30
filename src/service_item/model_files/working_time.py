# Contains WorkingTime and WorkingTimeException
# The first one is for weekly timetable fixes
# The second one - for single exceptions or annual works
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import datetime

# Return database filter to ServiceAbstract, Item

def get_children_for_service_item():
    pass

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
    # Set possible only to Item & ServiceAbstract
    content_type    = models.ForeignKey(
            ContentType, 
            on_delete = models.CASCADE, 
            #limit_choices_to = get_children_for_service_item,
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
    # Set possible only to Item & ServiceAbstract
    content_type    = models.ForeignKey(
            ContentType, 
            on_delete = models.CASCADE, 
            #limit_choices_to = get_children_for_service_item,
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

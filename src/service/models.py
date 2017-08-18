# coding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import time

# Create your models here.

# Set working hours on each weekday
class WorkingTime(models.Model):
    MONDAY      = 'Mon'
    TUESDAY     = 'Tue'
    WEDNESDAY   = 'Wed'
    THURSDAY    = 'Thu'
    FRIDAY      = 'Fri'
    SATURDAY    = 'Sat'
    SUNDAY      = 'Sun'
    EVERYDAY    = 'Eve'
    weekday     = models.CharField(max_length = 3, default = EVERYDAY, null = False, blank = False, verbose_name = 'Рабочее время', choices = (
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
    works_from  = models.TimeField(blank = False, null = False, default = time(0,0,0), verbose_name = 'Начало рабочего времени')
    works_to    = models.TimeField(blank = False, null = False, default = time(23,59,59), verbose_name = 'Конец рабочего времени')
    # Set possible only to Item & Service
    content_type    = models.ForeignKey(
            ContentType, 
            on_delete = models.CASCADE, 
            limit_choices_to = 
                models.Q(app_label = 'service', model = 'Service') 
                | models.Q(app_label = 'service', model = 'Item'), 
            blank = False, null = False, verbose_name = 'Тип назначения'
        )
    object_id       = models.PositiveIntegerField(blank = False, null = False, verbose_name = 'Id назначения')
    # Enables to set 'content_type' and 'object_id' by assigning
    # the destination object to this field:
    service         = GenericForeignKey('content_type', 'object_id')
    class Meta:
        verbose_name        = 'Время работы'
        verbose_name_plural = 'Расписания'
        ordering            = ['weekday']
        # Like OneToOne field for each model
        unique_together     = ('content_type', 'object_id')


class WorkingTimeException(models.Model):
    day_start   = models.DateField(blank = False, null = False, verbose_name = 'День исключения')
    duration    = models.IntegerField(blank = False, null = False, default = 1, verbose_name = 'Продолжительность')
    works_from  = models.TimeField(blank = False, null = False, default = time(0,0,0), verbose_name = 'Начало рабочего времени')
    works_to    = models.TimeField(blank = False, null = False, default = time(0,0,0), verbose_name = 'Конец рабочего времени')
    service     = models.OneToOneField('Service', on_delete = models.CASCADE, related_name = 'working_times', blank = False, null = False, verbose_name = 'Сервис')
    def is_weekend(self):
        return works_to - works_from < service.time_step
    class Meta:
        verbose_name        = 'Дата исключения'
        verbose_name_plural = 'Даты исключения'


class Service(models.Model):
    url_id      = models.CharField(max_length = 16, blank = False, null = False, unique = True, verbose_name = 'Фрагмент URL на английском')
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    description = models.CharField(max_length = 124, blank = False, null = False, verbose_name = 'Краткое описание')
    instruction = models.TextField(blank = True, null = True, verbose_name = 'Инструкция и подробное описание')    
    time_step   = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
    max_time_steps  = models.IntegerField(blank = False, null = False, default = 1, verbose_name = 'Максимальное число шагов времени непрерывного использования')
    default_price   = models.IntegerField(blank = True, null = True, verbose_name = 'Цена по-умолчанию за шаг времени', default = 0)
    edited      = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование этих данных')
    default_works_from  = models.TimeField(blank = False, null = False, default = time(0,0,0), verbose_name = 'Начало рабочего времени по-умолчанию')
    default_works_to    = models.TimeField(blank = False, null = False, default = time(23,59,59), verbose_name = 'Конец рабочего времени по-умолчанию')
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'


class Item(models.Model):
    # 'id' field will be added automatically 
    service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    price       = models.IntegerField(blank = True, null = True, verbose_name = 'Цена за шаг времени', default = 0)
    location    = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Расположение')
    extra_info  = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Доп. информация')
    is_active   = models.BooleanField(default = True, verbose_name = 'Работает')
    created     = models.DateTimeField(auto_now_add = True, null = False, verbose_name = 'Введено в строй')
    class Meta:
        verbose_name = 'Предмет сервиса'
        verbose_name_plural = 'Предметы сервиса'


class Order(models.Model):
    time_start  = models.DateTimeField(blank = False, null = False, unique = True, verbose_name = 'Время начала')
    time_end    = models.DateTimeField(blank = False, null = False, unique = True, verbose_name = 'Время конца')
    item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

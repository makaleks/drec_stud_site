# coding: utf-8
from django.db import models
from django.conf import settings
from datetime import time

# Create your models here.

class Service(models.Model):
    url_id      = models.CharField(max_length = 16, blank = False, null = False, unique = True, verbose_name = 'Фрагмент URL на английском')
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    description = models.CharField(max_length = 124, blank = False, null = False, verbose_name = 'Краткое описание')
    instruction = models.TextField(blank = True, null = True, verbose_name = 'Инструкция и подробное описание')    
    time_step   = models.TimeField(blank = False, null = False, verbose_name = 'Минимальное время использования (шаг времени)')
    max_time_steps  = models.IntegerField(blank = False, null = False, default = 1, verbose_name = 'Максимальное число шагов времени непрерывного использования')
    works_from  = models.TimeField(blank = False, null = False, default = time(0,0,0), verbose_name = 'Начало рабочего времени')
    works_to    = models.TimeField(blank = False, null = False, default = time(23,59,59), verbose_name = 'Конец рабочего времени')
    price       = models.IntegerField(blank = True, null = True, verbose_name = 'Цена по-умолчанию за шаг времени', default = 0)
    edited      = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование этих данных')
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'


class Item(models.Model):
    # 'id' field will be added automatically 
    service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', verbose_name = 'Сервис')
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
    item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', verbose_name = 'Предмет сервиса')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', verbose_name = 'Пользователь')
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

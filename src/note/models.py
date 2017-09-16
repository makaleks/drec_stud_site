# coding: utf-8
from django.db import models

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.SlugField(max_length = 16, blank = False, null = False, verbose_name = 'Название')
    text    = models.TextField(blank = True, verbose_name = 'Текст')
    order   = models.PositiveIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    class Meta:
        verbose_name        = 'Заметку'
        verbose_name_plural = 'Заметки'
        ordering            = ['order', 'name']


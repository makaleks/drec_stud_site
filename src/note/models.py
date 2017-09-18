# coding: utf-8
from django.db import models

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.SlugField(max_length = 16, blank = False, null = False, primary_key = True, verbose_name = 'Фрагмент URL на английском (навсегда)')
    text    = models.TextField(blank = True, verbose_name = 'Текст')
    class Meta:
        verbose_name        = 'Заметку'
        verbose_name_plural = 'Заметки'
        ordering            = ['name']


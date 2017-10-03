# coding: utf-8
from precise_bbcode.fields import BBCodeTextField
from django.db import models
from django.conf import settings

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.SlugField(max_length = 16, unique = True, blank = False, null = False, verbose_name = 'Название')
    text    = BBCodeTextField(max_length = 384, blank = True, null = False, verbose_name = 'Текст')
    order   = models.PositiveIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name        = 'Заметку'
        verbose_name_plural = 'Заметки'
        ordering            = ['order', 'name']

class Question(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'questions', blank = False, null = False, verbose_name = 'автор')
    created = models.DateTimeField(auto_now_add = True, null = False, verbose_name = 'Время создания')
    edited = models.DateTimeField(auto_now = True, null = False, verbose_name = 'Время редактирования', error_messages={'required':'heh'})
    title = models.CharField(max_length = 32, unique = True, blank = False, null = False, verbose_name = 'Заголовок')
    text = BBCodeTextField(blank = False, null = False, verbose_name = 'Текст')
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['created']

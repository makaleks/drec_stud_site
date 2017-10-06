# coding: utf-8
from django.db import models
from django.conf import settings
from django.urls import reverse
from datetime import datetime

# Create your models here.

class Survey(models.Model):
    title       = models.CharField(max_length = 64, blank = False, null = False, verbose_name = 'Заголовок')
    description = models.CharField(max_length = 256, blank = False, null = False, verbose_name = 'Описание')
    structure   = models.TextField(blank = False, null = False, verbose_name = 'Опрос в JSON (survey.js)')
    # Surveys can still be edited
    started     = models.DateTimeField(blank = False, null = True, verbose_name = 'Дата начала')
    finished    = models.DateTimeField(blank = False, null = True, verbose_name = 'Дата конца')
    def __str__(self):
        return self.title
    def is_started():
        return started and started > datetime.now()
    def is_finished():
        return started and finished
    def start(self, date_start = datetime.now(), date_end = None):
        self.started = start
        self.finished = end
        self.save(update_fields=['started', 'finished'])
    def get_absolute_url(self):
        return reverse('survey_detail', args = (self.pk,))
    def get_edit_url(self):
        return reverse('survey_edit', args=(self.pk,))
    class Meta:
        verbose_name        = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering            = ['-started']

class Answer(models.Model):
    answer  = models.TextField(blank = False, null = False, verbose_name = 'ответ в JSON (survey.js)')
    survey  = models.ForeignKey(Survey, on_delete = models.CASCADE, related_name = 'answers', verbose_name = 'Ответ')
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'answers', verbose_name = 'Пользователь')
    created = models.DateTimeField(auto_now = True, blank = False, null = False, verbose_name = 'Дата ответа')
    class Meta:
        verbose_name        = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering            = ['-created']

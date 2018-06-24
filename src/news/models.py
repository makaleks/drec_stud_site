# coding: utf-8
from django.db import models
from django.urls import reverse
from django.utils import timezone
from precise_bbcode.fields import BBCodeTextField

from utils.model_aliases import DefaultImageField

# Create your models here.

class News(models.Model):
    created = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    title   = models.CharField(max_length = 64, blank = False, null = False, verbose_name   = 'Заголовок')
    # Preview will be shown before spoiler
    text_preview = BBCodeTextField(blank = True, verbose_name = 'Превью')
    text    = BBCodeTextField(blank = True, verbose_name = 'Текст')
    image   = DefaultImageField(blank = True, null = True)
    # Useful + 'view on site' in /admin available
    def get_absolute_url(self):
        return '{0}?news={1}'.format(reverse('news:news-list'), self.id)
    def __str__(self):
        return '{0} (created {1})'.format(self.title, self.created.strftime('%Y-%m-%d %H:%M:%S') if self.created else timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
    class Meta:
        verbose_name        = 'Новость'
        verbose_name_plural = 'Новости'
        ordering            = ['-created']

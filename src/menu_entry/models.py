from django.db import models

# Create your models here.

class MenuEntry(models.Model):
    name = models.CharField(max_length = 16, unique = True, blank = False, null = False, verbose_name = 'Название раздела')
    url   = models.CharField(max_length = 64, unique = True, blank = False, null = False, verbose_name = 'Адрес')
    order      = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    class Meta:
        verbose_name = 'Элемент меню'
        verbose_name_plural = 'Элементы меню'
        ordering = ['order']


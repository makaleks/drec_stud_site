from django.db import models

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.CharField(max_length = 64, blank = False, null = False, primary_key = True)
    text    = models.TextField(blank = True, verbose_name = 'Текст')
    class Meta:
        verbose_name        = 'Заметку'
        verbose_name_plural = 'Заметки'
        ordering            = ['name']


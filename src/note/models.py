# coding: utf-8
from precise_bbcode.fields import BBCodeTextField
from django.db import models
from django.conf import settings

def get_default_approved():
    return settings.QUESTION_DEFAULT_APPROVED

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.CharField(max_length = 16, unique = True, blank = False, null = False, verbose_name = 'Название')
    slug    = models.SlugField(max_length = 16, blank = True, null = True, verbose_name = 'URL')
    text    = BBCodeTextField(blank = True, null = False, verbose_name = 'Текст')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
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
    is_public = models.BooleanField(default = True, null = False, verbose_name = 'Автор виден всем')
    is_approved = models.BooleanField(default = get_default_approved, blank = True, null = False, verbose_name = 'Одобрено')
    def __str__(self):
        return '{0}, {1}'.format(self.title, self.author)
    def get_absolute_url(self):
        return '/notes/student_council/{0}/'.format(self.id)
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['is_approved', 'created']

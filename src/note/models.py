# coding: utf-8
from precise_bbcode.fields import BBCodeTextField
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from comment.models import Comment

from utils.model_aliases import DefaultDocumentField

def get_default_approved():
    return settings.QUESTION_DEFAULT_APPROVED

# Create your models here.

class Note(models.Model):
    edited  = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    name    = models.CharField(max_length = 16, unique = True, blank = False, null = False, verbose_name = 'Название')
    slug    = models.SlugField(max_length = 16, blank = True, null = True, verbose_name = 'URL')
    text    = BBCodeTextField(blank = True, null = False, verbose_name = 'Текст')
    order   = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def get_absolute_url(self):
        #if self.slug != 'student_council':
        #    return reverse('note:note-id-detail', args=[self.id])
        #else:
        #    return reverse('note:note-slug-detail', args=[self.slug])
        return reverse('note:note-id-detail', args=[self.id])
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
    answers = GenericRelation(Comment, content_type_field = 'object_type', object_id_field = 'object_id')
    attachment   = DefaultDocumentField(blank = True, null = True, base_name = 'Дополнительное приложение')
    def __str__(self):
        return '{0}, {1}'.format(self.title, self.author)
    def get_absolute_url(self):
        return reverse('note:question-detail', args=[self.id])
    def get_answers(self):
        def _recursive(result, obj):
            result.append(obj)
            lst = list(obj.comments.all())
            for l in lst:
                _recursive(result, l)
        lst = list(self.answers.all())
        result = []
        for l in lst:
            _recursive(result, l)
        result.sort(key=lambda x: x.created)
        return result
    def is_staff_answered(self):
        answers = list(self.answers.all())
        for a in answers:
            if a.author.is_staff:
                return True
        return False
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['is_approved', '-created']

# coding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from utils.model_aliases import DefaultDocumentField

# Create your models here.

class Comment(models.Model):
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'comments')
    created = models.DateTimeField(auto_now_add = True, verbose_name = 'Время создания')
    edited = models.DateTimeField(auto_now_add = True, verbose_name = 'Время редактирования')
    text        = models.CharField(max_length = 512, blank = False, null = False, verbose_name = 'Текст')
    comments    = GenericRelation('comment.Comment',
                    content_type_field='object_type', 
                    object_id_field='object_id')
    object_type    = models.ForeignKey(
            ContentType, on_delete = models.CASCADE,
            limit_choices_to = 
                models.Q(app_label = 'comment', model = 'comment') | models.Q(app_label = 'note', model = 'question'),
            blank = False, null = False, verbose_name = 'Тип назначения')
    object_id      = models.PositiveIntegerField(blank = False, null = False, verbose_name = 'Id назначения')
    commented_object = GenericForeignKey('object_type', 'object_id')
    attachment   = DefaultDocumentField(blank = True, null = True, base_name = 'Дополнительное приложение')
    def __str__(self):
        return 'comment_by_{0}_{1}'.format(self.author.get_full_name().replace(' ', '_'), str(self.pk))
    def get_attachment_extention(self):
        return splitext(self.attachment.name)[1]
    def first_text(self):
        text = self.text;
        return text if len(text) <= 20 else text[:17] + '...'
    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'
        ordering = ('-created', )

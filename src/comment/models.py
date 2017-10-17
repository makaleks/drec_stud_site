# coding: utf-8
from django.db import models
from django.conf import settings
from djangp.contrib.contenttypes.fields import GenericForeignKey
from djangp.contrib.contenttypes.models import ContentType

# Create your models here.

class Comment(Interactive):
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'comments')
    create_date = models.DateField(auto_now_add = True, verbose_name = 'Время создания')
    edit_date = models.DateField(auto_now_add = True, verbose_name = 'Время редактирования')
    text        = models.CharField(max_length = 512, blank = False, null = False, verbose_name = 'Текст')
    comments    = GenericRelation('comment.Comment',
                    content_type_field='content_type', 
                    object_id_field='content_id')
    object_type    = models.ForeignKey(
            ContentType, on_delete = models.CASCADE,
            limit_choices_to = 
                models.Q(app_label = 'note', model = 'note'),
            blank = False, null = False, verbose_name = 'Тип назначения')
    object_id      = models.PositiveIntegerField(blank = False, null = False, verbose_name = 'Id назначения')
    commented_object = GenericForeignKey('content_type', 'content_id')
    def __str__(self):
        return 'comment_by_{0}_{1}'.format(author.get_full_name().replace(' ', '_'), str(self.pk))
    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'
        ordering = ('-create_date', )

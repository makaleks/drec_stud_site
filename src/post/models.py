# coding: utf-8
from django.db import models

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length = 64, verbose_name = u'Заголовок')
    text = models.TextField(verbose_name = u'Текст')
    # blank=True: allow no image (text-only post)
    image = models.ImageField(blank = True, verbose_name = u'Картинка')
    create_date = models.DateField(auto_now_add = True)
    edit_date = models.DateField(auto_now_add = True)
    # sets appeal at /admin/
    def __unicode__(self):
        return "post_" + str(self.pk)

    class Meta:
        verbose_name = u'Пост'
        verbose_name_plural = u'Посты'
        ordering = ('-create_date', )

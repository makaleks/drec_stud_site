from django.db import models

# Create your models here.

class News(models.Model):
    created = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    edited = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование')
    title = models.CharField(max_length = 64, blank = False, null = False, verbose_name = 'Заголовок')
    # Preview will be shown before spoiler
    text_preview = models.TextField(blank = True, verbose_name = 'Превью')
    text = models.TextField(blank = True, verbose_name = 'Текст')
    image = models.ImageField(blank = True)
    # Useful + 'view on site' in /admin available
    def get_absolute_url(self):
        return '/?news={}'.format(self.id)
    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-edited']

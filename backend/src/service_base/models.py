#
# HOW TO USE ServiceBase:
# 1) Inherit your model from ServiceBase
# 2) Add to your model a OneToOneField(parent_link = True, related_name = 'child_obj') field with name 'parent_obj'
# 3) When writing views, set [context_object_name = 'service'] - this is required for template inheritance
#
#######################################################################
#                                                                     #
# !! ALL OTHER ServiceBase OBJECTS WILL BE DELETED AT SERVER START !! #
#                                                                     #
#######################################################################
#

from django.db import models
from django.conf import settings

from precise_bbcode.fields import BBCodeTextField

from utils.model_aliases import DefaultImageField

# Create your models here.

class ServiceBase(models.Model):
    name        = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Название')
    location    = models.CharField(max_length = 124, blank = True, null = True, verbose_name = 'Расположение')
    instruction = BBCodeTextField(blank = True, null = True, verbose_name = 'Инструкция и описание')
    image       = DefaultImageField(blank = False, null = False)
    edited      = models.DateTimeField(auto_now = True, verbose_name = 'Последнее редактирование этих данных')
    is_active   = models.BooleanField(default = True, blank = False, null = False, verbose_name = 'Работает')
    responsible_user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = 'Ответственное лицо')
    responsible_room    = models.CharField(max_length = 32, blank = True, null = True, verbose_name = 'Комната ответственного')
    def __str__(self):
        return '{0}(id={1})'.format(self.name, self.id)
    class Meta:
        abstract = True


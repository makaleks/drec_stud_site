# coding: utf-8
from django.db import models
from service.models import Service
# Uncomment to enable #passwordAuth
#from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager

# Create your models here.


# Replace next string with this one to enable #passwordAuth
#class User(AbstractBaseUser):
class User(models.Model):
    first_name      = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Имя')
    last_name       = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Фамилия')
    patronymic_name = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Отчество')
    # Two 'blank' (unrequired) values can`t be unique
    phone_number    = models.CharField(max_length = 20, blank = False, null = False, unique = False, verbose_name = 'Контактный номер')
    account_id      = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Аккаунт')
    group_number    = models.CharField(max_length = 4, blank = False, null = False, verbose_name = 'Номер группы')
    account         = models.PositiveSmallIntegerField(default = 0, blank = True, null = False, verbose_name = 'Счёт')
    avatar_url      = models.URLField(null = True, blank = True)
    # Two 'blank' (unrequired) values can`t be unique
    email           = models.CharField(default = '', max_length = 64, blank = True, null = False, unique = False, verbose_name = 'Почта')
    USERNAME_FIELD  = 'phone_number'
    EMAIL_FIELD     = 'email'
    # USERNAME_FIELD and password are always required
    REQUIRED_FIELDS = ['last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email']
    is_superuser    = models.BooleanField(default = False, verbose_name = 'Разработчик')
    is_staff        = models.BooleanField(default = False, verbose_name = 'Администратор')
    is_active       = models.BooleanField(default = True)
    # uid is the info from plastic card
    # TODO: in production make this field REQUIRED
    uid             = models.CharField(max_length = 128, blank = True, null = True, verbose_name = 'UID карты')
    # Comment to enable #passwordAuth (start)
    is_anonymous    = models.BooleanField(default = False)
    is_authenticated= models.BooleanField(default = True)
    last_login      = models.DateTimeField(default = None, null = True, blank = True)
    # Comment (end)
    objects         = UserManager()
    def has_perm(self, perm, obj=None):
        pass
    def has_module_perm(self, app_label):
        pass
    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)
    def get_short_name(self):
        return self.first_name
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True
    def __str__(self):
        return '{0} (id={1})'.format(self.get_full_name(), self.id)
    class Meta:
        ordering            = ['is_superuser', 'is_staff', 'group_number', 'last_name']
        verbose_name        = 'Пользователя'
        verbose_name_plural = 'Пользователи'

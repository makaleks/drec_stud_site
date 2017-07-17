# coding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager

# Create your models here.


class User(AbstractBaseUser):
    first_name      = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Имя')
    last_name       = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Фамилия')
    patronymic_name = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Отчество')
    phone_number    = models.CharField(max_length = 20, blank = False, null = False, unique = True, verbose_name = 'Контактный номер')
    account_url     = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Аккаунт')
    # Two 'blank' (unrequired) values can`t be unique
    email           = models.CharField(max_length = 64, blank = True, null = False, unique = False, verbose_name = 'Почта')
    USERNAME_FIELD  = 'phone_number'
    EMAIL_FIELD     = 'email'
    # USERNAME_FIELD and password are always required
    REQUIRED_FIELDS = ['last_name', 'first_name', 'patronymic_name', 'account_url', 'email']
    is_superuser    = models.BooleanField(default = False)
    is_staff        = models.BooleanField(default = False)
    is_active       = models.BooleanField(default = True)
    objects         = UserManager()
    def has_perm(self, perm, obj=None):
        pass
    def has_module_perm(self, app_label):
        pass
    def get_full_name():
        return "{0} {1}".format(first_name, last_name)
    def get_short_name():
        return first_name
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

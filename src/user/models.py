# coding: utf-8
from django.db import models
# Uncomment to enable #passwordAuth
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db.models import Q
from service.models import Service
from survey.models import Survey, Answer
from .managers import UserManager

# Create your models here.

def make_random_password():
    return User.objects.make_random_password(length = 20)

# Replace next string with this one to enable #passwordAuth
class User(AbstractBaseUser, PermissionsMixin):
#class User(models.Model):
    first_name      = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Имя')
    last_name       = models.CharField(max_length = 32, blank = False, null = False, verbose_name = 'Фамилия')
    patronymic_name = models.CharField(max_length = 32, default = '', blank = True, null = True, verbose_name = 'Отчество')
    # Two 'blank' (unrequired) values can`t be unique
    phone_number    = models.CharField(max_length = 20, default = '', blank = True, null = True, unique = False, verbose_name = 'Контактный номер')
    account_id      = models.CharField(max_length = 64, blank = False, null = False, unique = True, verbose_name = 'Аккаунт')
    group_number    = models.CharField(max_length = 4, blank = False, null = False, verbose_name = 'Номер группы')
    account         = models.DecimalField(default = 0, max_digits = 7, decimal_places = 2, blank = False, null = False, verbose_name = 'Счёт')
    avatar_url      = models.URLField(null = True, blank = True, verbose_name = 'URL аватарки')
    # Two 'blank' (unrequired) values can`t be unique
    email           = models.CharField(default = '', max_length = 64, blank = True, null = False, unique = False, verbose_name = 'Почта')
    USERNAME_FIELD  = 'account_id'
    EMAIL_FIELD     = 'email'
    # USERNAME_FIELD and password are always required
    REQUIRED_FIELDS = ['last_name', 'first_name', 'patronymic_name', 'group_number', 'phone_number', 'email']
    is_superuser    = models.BooleanField(default = False, verbose_name = 'Разработчик')
    is_staff        = models.BooleanField(default = False, verbose_name = 'Доступ к админке')
    is_active       = models.BooleanField(default = True)
    # uid is the info from plastic card
    # TODO: in production make this field REQUIRED
    card_uid        = models.CharField(max_length = 128, blank = True, null = True, verbose_name = 'UID карты')
    # Comment to enable #passwordAuth (start)
    #is_anonymous    = models.BooleanField(default = False)
    #is_authenticated= models.BooleanField(default = True)
    #last_login      = models.DateTimeField(default = None, null = True, blank = True)
    # Comment (end)
    objects         = UserManager()
    # Password hash requires 128 characters
    # Uncomment to enable #passwordAuth
    password        = models.CharField(default = make_random_password, max_length = 128, verbose_name = 'Хэш резервного пароля')
    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)
    def get_short_name(self):
        return self.first_name
    def __str__(self):
        return '{0} (id={1})'.format(self.get_full_name(), self.id)
    def get_surveys_to_pass(self):
        now = timezone.now()
        passed = self.answers.filter(Q(survey__started__lte = now) & Q(survey__finished__gt = now)).values_list('survey__id', flat = True)
        actual = Survey.objects.filter(Q(started__lte = now) & Q(finished__gt = now))
        return actual.exclude(id__in = passed).count()
        #return Survey.objects.filter(
    class Meta:
        ordering            = ['is_superuser', 'is_staff', 'group_number', 'last_name']
        verbose_name        = 'Пользователя'
        verbose_name_plural = 'Пользователи'

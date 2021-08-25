# coding: utf-8
from django.db import models
# Uncomment to enable #passwordAuth
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.conf import settings

from service.models import Service
from survey.models import Survey, Answer
from utils.utils import check_unique, get_id_by_url_vk

import datetime
import re

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
    group_number    = models.CharField(max_length = 10, blank = False, null = False, verbose_name = 'Номер группы')
    room_number     = models.CharField(max_length = 7, blank = True, null = True, verbose_name = 'Номер комнаты')
    account         = models.DecimalField(default = 0, max_digits = 7, decimal_places = 2, blank = False, null = False, verbose_name = 'Счёт')
    avatar_url      = models.URLField(max_length = 300, null = True, blank = True, verbose_name = 'URL аватарки')
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
    def get_all_data(self):
        return {
                'first_name':      self.first_name,
                'last_name':       self.last_name,
                'patronymic_name': self.patronymic_name,
                'phone_number':    self.phone_number,
                'account_id':      self.account_id,
                'group_number':    self.group_number,
                'account':         self.account,
                'email':           self.email,
                'is_staff':        self.is_staff,
                'is_active':       self.is_active,
                'card_uid':        self.card_uid,
        }
    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)
    def get_short_name(self):
        return self.first_name
    def __str__(self):
        return '{0} (id={1})'.format(self.get_full_name(), self.id)
    def get_surveys_to_pass(self):
        now = datetime.datetime.now()
        passed = self.answers.filter(Q(survey__started__lte = now) & Q(survey__finished__gt = now)).values_list('survey__id', flat = True)
        actual = Survey.objects.filter(Q(started__lte = now) & Q(finished__gt = now))
        return actual.exclude(id__in = passed).count()
        #return Survey.objects.filter(
    def get_all_errors(self, skip_account_check = False):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        if self.patronymic_name:
            self.patronymic_name = self.patronymic_name.strip()
        if self.phone_number:
            self.phone_number = self.phone_number.strip()
        if self.email:
            self.email = self.email.strip()
        self.account_id = self.account_id.strip()
        self.group_number = self.group_number.strip()
        if self.room_number:
            self.room_number = self.room_number.strip()
        if self.card_uid:
            self.card_uid = self.card_uid.strip()
        # In other case, Faculty import will fail
        from utils.validators import is_valid_name, is_valid_email, is_valid_group, is_valid_group, is_valid_phone

        errors = {}
        def append_error(key, s):
            if key in errors:
                errors[key] = errors[key] + '\n' + s
            else:
                errors.update({key: s})

        # Format of phone_number (optional)
        if self.phone_number and is_valid_phone(self.phone_number) is False:
            append_error('phone_number', 'Неверный формат телефонного номера')
        # Format of name
        if is_valid_name(self.last_name) is False:
            append_error('last_name', 'Неверный формат фамилии')
        if is_valid_name(self.first_name) is False:
            append_error('first_name', 'Неверный формат имени')
        if self.patronymic_name and is_valid_name(self.patronymic_name) is False:
            append_error('patronymic_name', 'Неверный формат отчества')
        # Format of group
        if is_valid_group(self.group_number) is False:
            append_error('group_number', 'Неверный формат группы')
        # Format of email (optional)
        if self.email and (is_valid_email(self.email) is False):
            append_error('email', 'Неверный формат почты')

        # Unique phone
        if self.phone_number:
            user = check_unique(User, 'phone_number', self.phone_number)
            if user and user.pk != self.pk:
                append_error('phone_number', 'Этот номер телефона уже зарегистрировал {0} из {1} группы'.format(user.get_full_name(), user.group_number))
        # Unique and valid account_id
        if not skip_account_check and not settings.IS_ID_RECOGNITION_BROKEN_VK and not settings.IS_EMERGENCY_LOGIN_MODE:
            id_num = get_id_by_url_vk(self.account_id)
            if not id_num:
                append_error('account_id', 'Не удалось получить id из социальной сети. Это точно существующий пользователь?')
            else:
                self.account_id = id_num
        elif not self.account_id.isdigit():
            append_error('account_id', 'Аккаунт должен иметь численное представление!')
        user = check_unique(User, 'account_id', self.account_id)
        if user and user.pk != self.pk:
            append_error('account_id', 'Эту ссылку на аккаунт уже зарегистрировал {0} из {1} группы'.format(user.get_full_name(), user.group_number))
        # Unique email (optional)
        if len(self.email) != 0:
            user = check_unique(User, 'email', self.email)
            if user and user.pk != self.pk:
                append_error('email', 'Эту почту уже зарегистрировал {0} из {1} группы'.format(user.get_full_name(), user.group_number))
        return errors
    def clean(self):
        errors = self.get_all_errors()
        if errors:
            raise ValidationError(errors)
    def save(self, no_clean = False, *args, **kwargs):
        if not no_clean:
            self.full_clean()
        return super(User, self).save(*args, **kwargs)
    class Meta:
        ordering            = ['is_superuser', 'is_staff', 'group_number', 'last_name']
        verbose_name        = 'Пользователя'
        verbose_name_plural = 'Пользователи'

# Be careful!
class Faculty(models.Model):
    name  = models.CharField(max_length = 8, blank = False, null = False, verbose_name = 'Имя (кратко)')
    groups = models.CharField(max_length = 128, blank = False, null = False, verbose_name = 'Группы:\',\'-разделитель,\'_\'-любое число')
    def is_group_in_faculty(self, s):
        if s is None or s == '':
            return False
        patterns = [re.escape(s).replace('_', '[0-9]') for s in self.groups.split(',')]

        for i in range(len(patterns)):
            # Add possible subgroup char, like '419a' of '419b'
            patterns[i] = '^' + patterns[i] + '\w?$'
        for p in patterns:
            if re.match(p, s):
                return True
        return False
    def __str__(self):
        return self.name
    def clean(self):
        from utils.validators import is_valid_faculty
        if is_valid_faculty(self.groups) is False:
            raise ValidationError({'groups': 'Неверный формат групп факультета'})
    def save(self, *args, **kwargs):
        # Remove whitespaces
        self.groups.replace(' ', '')
        # Validate
        self.full_clean()
        return super(Faculty, self).save(*args, **kwargs)
    class Meta:
        verbose_name        = 'Факультет'
        verbose_name_plural = 'Факультеты'


class MoneyTransaction(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        db_column='user_id',
        blank=False, null=False, verbose_name='На чей user_id пришли деньги'
    )
    registered_at = models.DateTimeField(blank=False, null=False, verbose_name='Когда была зарегистрирована')
    money_came = models.FloatField(blank=False, null=False, verbose_name='Сколько пришло денег')
    source = models.CharField(max_length=10, blank=True, null=True, verbose_name='Из какого источника пришли деньги')

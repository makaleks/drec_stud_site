from django.contrib import admin
from reversion.admin import VersionAdmin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Uncomment to enable #passwordAuth
#from django.contrib.auth.forms import ReadOnlyPasswordHashField

from utils.validators import *
from utils.utils import check_unique
from .models import User

import logging
logger = logging.getLogger('site_events')

# Register your models here.

class UserCreationForm(forms.ModelForm):
    # Uncomment to enable #passwordAuth
    #password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput)
    #password2 = forms.CharField(label = 'Password confirmation', widget = forms.PasswordInput)

    def clean(self):
        phone_number    = self.cleaned_data.get('phone_number')
        last_name       = self.cleaned_data.get('last_name')
        first_name      = self.cleaned_data.get('first_name')
        patronymic_name = self.cleaned_data.get('patronymic_name')
        group_number    = self.cleaned_data.get('group_number')
        account_id      = self.cleaned_data.get('account_id')
        email           = self.cleaned_data.get('email')
        if is_valid_phone(phone_number) is False:
            raise forms.ValidationError('Неверный формат телефонного номера')
        if is_valid_name(last_name) is False:
            raise forms.ValidationError('Неверный формат фамилии')
        if is_valid_name(first_name) is False:
            raise forms.ValidationError('Неверный формат имени')
        if is_valid_name(patronymic_name) is False:
            raise forms.ValidationError('Неверный формат отчества')
        if is_valid_group(group_number) is False:
            raise forms.ValidationError('Неверный формат группы')
        # 'email' is optional
        if (len(email) != 0) and (is_valid_email(email) is False):
            raise forms.ValidationError('Неверный формат почты')

        if check_unique(User, 'phone_number', phone_number) is False:
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        if check_unique(User, 'account_id', account_id) is False:
            raise forms.ValidationError('Эта ссылка на аккаунт уже зарегистрирована')
        if (len(email) != 0) and (check_unique(User, 'email', email) is False):
            raise forms.ValidationError('Эта почта уже зарегистрирована')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email')
    # Uncomment to enable #passwordAuth
    #def clean_password2(self):
    #    # Check if 2 passwords are the same
    #    password1 = self.cleaned_data.get('password1')
    #    password2 = self.cleaned_data.get('password2')
    #    if password1 and password2 and password1 != password2:
    #        raise forms.ValidationError('Passwords don`t match')
    #    return password2
    #def save(self, commit = True):
    #    # Save password in hashed format
    #    user = super(UserCreationForm, self).save(commit=False)
    #    user.set_password(self.cleaned_data['password1'])
    #    if commit:
    #        user.save()
    #    return user

class UserChangeForm(forms.ModelForm):
    # Uncomment to enable #passwordAuth
    #password = ReadOnlyPasswordHashField()

    def clean(self):
        phone_number    = self.cleaned_data.get('phone_number')
        last_name       = self.cleaned_data.get('last_name')
        first_name      = self.cleaned_data.get('first_name')
        patronymic_name = self.cleaned_data.get('patronymic_name')
        group_number    = self.cleaned_data.get('group_number')
        account_id      = self.cleaned_data.get('account_id')
        email           = self.cleaned_data.get('email')
        if is_valid_phone(phone_number) is False:
            raise forms.ValidationError('Неверный формат телефонного номера')
        if is_valid_name(last_name) is False:
            raise forms.ValidationError('Неверный формат фамилии')
        if is_valid_name(first_name) is False:
            raise forms.ValidationError('Неверный формат имени')
        if is_valid_name(patronymic_name) is False:
            raise forms.ValidationError('Неверный формат отчества')
        if is_valid_group(group_number) is False:
            raise forms.ValidationError('Неверный формат группы')
        # 'email' is optional
        if (len(email) != 0) and (is_valid_email(email) is False):
            raise forms.ValidationError('Неверный формат почты')

        if ((check_unique(User, 'phone_number', phone_number) is False)
            and (phone_number != self.instance.phone_number)):
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        if ((check_unique(User, 'account_id', account_id) is False)
            and (account_id != self.instance.account_id)):
            raise forms.ValidationError('Эта ссылка на аккаунт уже зарегистрирована')
        if (len(email) != 0) and (check_unique(User, 'email', email) is False) and email != self.instance.email:
            raise forms.ValidationError('Эта почта уже зарегистрирована')
        # Uncomment to enable #passwordAuth
        #self.cleaned_data['password'] = self.instance.password
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email')
    # Uncomment to enable #passwordAuth
    #def clean_password2(self):
    #    # Regardless of what the user provides, return the initial value.
    #    # This is done here, rather than on the field, because the
    #    # field does not have access to the initial value
    #    return self.initial['password']


class UserAdmin(BaseUserAdmin, VersionAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'is_staff')
    list_filter = ('is_staff', 'group_number')
    fieldsets = (
        # Uncomment to enable #passwordAuth
        #(None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account')}),
        # Replace next string with this one to enable #passwordAuth
        #('Contacts', {'fields': ('account_id', 'email')}),
        ('Contacts', {'fields': ('account_id', 'uid', 'phone_number', 'email')}),
        ('Permissions', {'fields': ('is_active','is_staff',)}),
    )
    # Superuser can be created only from tty
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Replace next string with this one to enable #passwordAuth
            #'fields': ('phone_number', 'last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email', 'is_staff', 'password1', 'password2')}
            'fields': ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'uid', 'phone_number', 'email', 'is_staff')}
        ),
    )
    search_fields = ('last_name', 'group_number', 'phone_number', 'account_id', 'first_name', 'patronymic_name', 'email',)
    filter_horizontal = ()
    ordering = ['-is_superuser', '-is_staff', 'group_number', 'last_name', 'first_name', 'patronymic_name']
    def save_model(self, request, obj, form, change):
        if change:
            fields = [{field: str(getattr(obj, field))} for field in form.changed_data]
            logger.info('{0} was {1}'.format(self.model.__name__,  'edited in {0}'.format(str(fields)) if fields else 'just saved'), extra={'user': request.user.get_full_name()})
        else:
            fields = [{f.name: str(getattr(obj, f.name))} for f in obj._meta.fields]
            logger.info('{0} was created as {1}'.format(self.model.__name__, str(fields)), extra={'user': request.user.get_full_name()})
        super(UserAdmin, self).save_model(request, obj, form, change)

# Register the new UserAdmin
admin.site.register(User, UserAdmin)
# No permissions for now
admin.site.unregister(Group)

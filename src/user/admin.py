from django.contrib import admin
from reversion.admin import VersionAdmin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings
# Uncomment to enable #passwordAuth
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from utils.validators import *
from utils.utils import check_unique, get_id_by_url_vk
from .models import User, Faculty

import logging
logger = logging.getLogger('site_events')

# Register your models here.

class UserCreationForm(forms.ModelForm):
    # Uncomment to enable #passwordAuth
    #password1 = forms.CharField(label = 'Пароль', widget = forms.PasswordInput)
    #password2 = forms.CharField(label = 'Подтверждение пароля', widget = forms.PasswordInput)

    groups = forms.ModelMultipleChoiceField(label='Группы',required=False,widget=FilteredSelectMultiple('Группы',is_stacked=False),queryset=Group.objects.all())
    def clean(self):
        pass

    class Meta:
        model = User
        exclude = []
        #fields = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email')
    # Uncomment all the following to enable #passwordAuth
    #def clean_password2(self):
    #    # Check if 2 passwords are the same
    #    password1 = self.cleaned_data.get('password1')
    #    password2 = self.cleaned_data.get('password2')
    #    if password1 and password2 and password1 != password2:
    #        raise forms.ValidationError('Пароли не совпадают')
    #    return password2
    #def save(self, commit = True):
    #    # Save password in hashed format
    #    user = super(UserCreationForm, self).save(commit=False)
    #    user.set_password(self.cleaned_data['password1'])
    #    if commit:
    #        user.save()
    #    return user
    # Uncomment end

class UserChangeForm(forms.ModelForm):
    # Uncomment to enable #passwordAuth
    password = ReadOnlyPasswordHashField(label='Хэш от пароля')

    groups = forms.ModelMultipleChoiceField(label='Группы',required=False,widget=FilteredSelectMultiple('Группы',is_stacked=False),queryset=Group.objects.all())
    def clean(self):
        # Uncomment to enable #passwordAuth
        #self.cleaned_data['password'] = self.instance.password
        return self.cleaned_data

    class Meta:
        model = User
        exclude = []
        #fields = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'account_id', 'email')
    # Uncomment to enable #passwordAuth
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class UserAdmin(BaseUserAdmin, VersionAdmin):
    history_latest_first = True
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('last_name', 'first_name', 'patronymic_name', 'group_number', 'is_staff')
    list_filter = ('is_staff', 'groups', 'group_number')
    fieldsets = (
        # Uncomment to enable #passwordAuth
        #(None, {'fields': ('phone_number', 'password')}),
        ('Личная информация', {'fields': ('last_name', 'first_name', 'patronymic_name', 'group_number', 'room_number', 'account', 'avatar_url')}),
        # Replace next string with this one to enable #passwordAuth
        #('Contacts', {'fields': ('account_id', 'email')}),
        ('Контакты', {'fields': ('account_id', 'card_uid', 'phone_number', 'email')}),
        ('Права', {'fields': ('is_active','is_staff','password','groups')}),
    )
    # Superuser can be created only from tty
    add_fieldsets = (
        (None, {
            # Just sets larger alignment
            'classes': ('wide',),
            'fields': ('last_name','first_name','patronymic_name',
                'group_number',
                'room_number',
                # Uncomment to enable #passwordAuth
                #'account_id','password1','password2','card_uid',
                'account_id','card_uid',
                'phone_number','email',
                'is_staff','groups',
                'avatar_url')}
        ),
    )
    add_form_template = 'admin/user/user/change_form.html'
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
#admin.site.unregister(Group)

@admin.register(Faculty)
class FacultyAdmin(VersionAdmin):
    history_latest_first = True


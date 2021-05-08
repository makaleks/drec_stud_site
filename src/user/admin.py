from django.contrib import admin
from reversion.admin import VersionAdmin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings
# Uncomment to enable #passwordAuth
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponseRedirect
from django.db import transaction

from utils.validators import *
from utils.utils import check_unique, get_id_by_url_vk
from .models import User, Faculty

import json

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
    change_list_template = 'admin/user/user/change_list.html'
    def save_model(self, request, obj, form, change):
        if change:
            fields = [{field: str(getattr(obj, field))} for field in form.changed_data]
            logger.info('{0} was {1}'.format(self.model.__name__,  'edited in {0}'.format(str(fields)) if fields else 'just saved'), extra={'user': request.user.get_full_name()})
        else:
            fields = [{f.name: str(getattr(obj, f.name))} for f in obj._meta.fields]
            logger.info('{0} was created as {1}'.format(self.model.__name__, str(fields)), extra={'user': request.user.get_full_name()})
        super(UserAdmin, self).save_model(request, obj, form, change)
    def get_urls(self):
        urls = super(UserAdmin, self).get_urls()
        to_add = [
            path('add_many/', self.admin_site.admin_view(self.add_many)),
        ]
        return to_add + urls
    def add_many(self, request):
        #import datetime
        #time_start = datetime.datetime.now()
        #print('\n\n###\n1. add_many START at {}'.format(time_start))
        perms = {
            'has_add_permission':    self.has_add_permission(request),
            #'has_delete_permission': self.has_delete_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_view_permission':   self.has_view_permission(request),
            # required to show Welcome
            'has_permission': True,
        }
        if not all(perms.values()) or not request.user.is_staff:
            raise Http404()
        required_fields_dicts = {
                'Имя': 'first_name',
                'Фамилия': 'last_name',
                'Номер группы': 'group_number',
                'Аккаунт ВК': 'account_id',
        }
        required_fields = list(required_fields_dicts.keys())
        # Here I excluded 'card_uid', to test if no one needs it :)
        optional_fields_dicts = {
                'Отчество': 'patronymic_name',
                'Номер комнаты': 'room_number',
                'Номер телефона': 'phone_number',
                'Email': 'email',
        }
        optional_fields = list(optional_fields_dicts.keys())
        all_fields = {**required_fields_dicts, **optional_fields_dicts}
        context = {
            'opts': User._meta,
            'site_url': '/',
            'required_fields': json.dumps(required_fields),
            'account_id_field': json.dumps(required_fields[list(required_fields_dicts.values()).index('account_id')]),
            'optional_fields': json.dumps(optional_fields),
        }
        context.update(perms)
        if request.method == 'POST':
            status_texts = {
                'success': {
                    'type': 'success', 
                    'text': 'Пользователи успешно добавлены!',
                },
                'process': {
                    'type': 'info',
                    'text': 'Исправьте ошибки и отправьте на повторную проверку',
                },
                'ready': {
                    'type': 'primary',
                    'text': 'Проверки пройдены! Проверьте порядок колонок и отсутствие мусора в данных. Если всё в порядке - отправляйте на сохранение!',
                },
                'error': {
                    'type': 'danger',
                    'text': 'Что-то пошло не так',
                },
            }
            status = status_texts['error']
            source = request.POST.dict()
            # START prepare data
            values_dict = {}
            keys_dict = {}
            checked_and_locked_source = []
            for s_key,s_value in source.items():
                if s_key[:6] == 'column':
                    pos = int(s_key[7:])
                    keys_dict[pos] = s_value
                elif s_key[:18] == 'checked_and_locked':
                    checked_and_locked_source.append(bool(s_value))
                elif s_key[:5] == 'value':
                    [y,x] = s_key.split('-')[1:]
                    y = int(y)
                    x = int(x)
                    if not y in values_dict:
                        values_dict[y] = {}
                    values_dict[y][x] = s_value
            keys = [keys_dict[i_key] for i_key in sorted(keys_dict)]
            already_checked_and_locked = False if False in checked_and_locked_source else True
            for k in values_dict:
                values_dict[k] = [
                        values_dict[k][i_key] 
                                for i_key in sorted(values_dict[k])
                ]
            values = [values_dict[i_key] for i_key in sorted(values_dict)]
            # reserve array view for context
            context_values = [{'checked_and_locked': True, 'values': v} for v in values]
            # convert to dict to use named parameters in User constructor
            for (v,i) in zip(values,range(len(values))):
                values[i] = {
                        all_fields[key]: value 
                                for (key,value) in zip(keys,values[i])
                }
            # STOP prepare data
            # now validate
            #time_validate = datetime.datetime.now()
            #print('2. validation start at {}'.format(time_validate))
            #print('    timedelta = {}'.format(time_validate - time_start))
            validation_errors = []
            users = [User(**v) for v in values]
            for i in range(len(values)):
                u = users[i]
                # Hope all users are checked on client-side
                # (Takes too much time to request all Vk accounts)
                e = u.get_all_errors(skip_account_check = True)
                for j in range(len(users)):
                    if j != i and users[j].account_id == u.account_id:
                        s = 'Этот аккаунт совпадает с аккаунтом в строке {0} ({1})'.format(j + 1, users[j].get_full_name())
                        if 'account_id' in e:
                            e['account_id'] = e['account_id'] + '\n' + s
                        else:
                            e.extend({'account_id': s})
                if e:
                    context_values[i]['checked_and_locked'] = False
                    validation_errors.append({'line': i+1, 'errors': list(e.values())})
                    status = status_texts['process']
            extra_context = {
                'validation_errors': validation_errors,
                'user_data': context_values,
                'column_names': keys,
            }
            #time_save = datetime.datetime.now()
            #print('3. validation start at {}'.format(time_save))
            #print('    timedelta = {}'.format(time_save - time_validate))
            #print('    start td  = {}'.format(time_save - time_start))
            if not validation_errors and already_checked_and_locked:
                try:
                    with transaction.atomic():
                        #print('I AM SAVING !')
                        for v in values:
                            User(**v).save(no_clean = True)
                    # Well done!
                    status = status_texts['success']
                    extra_context['user_data'] = []
                    extra_context['column_names'] = []
                except Exception as e:
                    print(e)
                    extra_context['validation_errors'].append('Что-то пошло не так, пользователи не добавлены\n{0}'.format(str(e)))
                    status = status_texts['error']
            elif not validation_errors:
                status = status_texts['ready']
            extra_context['status'] = json.dumps(status);
            extra_context['validation_errors'] = json.dumps(extra_context['validation_errors']);
            extra_context['user_data'] = json.dumps(extra_context['user_data'])
            extra_context['column_names'] = json.dumps(extra_context['column_names'])
            context.update(extra_context)

            #time_done = datetime.datetime.now()
            #print('4. finish at {}\n###\n\n'.format(time_done))
            #print('    timedelta = {}'.format(time_done - time_save))
            #print('    start td  = {}'.format(time_done - time_start))
        return render(request, 'admin/user/user/add_many.html', context)

# Register the new UserAdmin
admin.site.register(User, UserAdmin)
# No permissions for now
#admin.site.unregister(Group)

@admin.register(Faculty)
class FacultyAdmin(VersionAdmin):
    history_latest_first = True


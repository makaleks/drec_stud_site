from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from utils.validators import is_valid_name, is_valid_phone, is_valid_email
from utils.utils import check_unique
from .models import User

# Register your models here.

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Password confirmation', widget = forms.PasswordInput)

    def clean(self):
        phone_number    = self.cleaned_data.get('phone_number')
        last_name       = self.cleaned_data.get('last_name')
        first_name      = self.cleaned_data.get('first_name')
        patronymic_name = self.cleaned_data.get('patronymic_name')
        account_id     = self.cleaned_data.get('account_id')
        email           = self.cleaned_data.get('email')
        if is_valid_phone(phone_number) is False:
            raise forms.ValidationError('Неверный формат телефонного номера')
        if is_valid_name(last_name) is False:
            raise forms.ValidationError('Неверный формат фамилии')
        if is_valid_name(first_name) is False:
            raise forms.ValidationError('Неверный формат имени')
        if is_valid_name(patronymic_name) is False:
            raise forms.ValidationError('Неверный формат отчества')
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
        fields = ('last_name', 'first_name', 'patronymic_name', 'account_id', 'email')
    def clean_password2(self):
        # Check if 2 passwords are the same
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don`t match')
        return password2
    def save(self, commit = True):
        # Save password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    def clean(self):
        phone_number    = self.cleaned_data.get('phone_number')
        last_name       = self.cleaned_data.get('last_name')
        first_name      = self.cleaned_data.get('first_name')
        patronymic_name = self.cleaned_data.get('patronymic_name')
        account_id     = self.cleaned_data.get('account_id')
        email           = self.cleaned_data.get('email')
        if is_valid_phone(phone_number) is False:
            raise forms.ValidationError('Неверный формат телефонного номера')
        if is_valid_name(last_name) is False:
            raise forms.ValidationError('Неверный формат фамилии')
        if is_valid_name(first_name) is False:
            raise forms.ValidationError('Неверный формат имени')
        if is_valid_name(patronymic_name) is False:
            raise forms.ValidationError('Неверный формат отчества')
        # 'email' is optional
        if (len(email) != 0) and (is_valid_email(email) is False):
            raise forms.ValidationError('Неверный формат почты')

        if ((check_unique(User, 'phone_number', phone_number) is False)
            and (phone_number != self.instance.phone_number)):
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        if ((check_unique(User, 'account_id', account_id) is False)
            and (account_id != self.instance.account_id)):
            raise forms.ValidationError('Эта ссылка на аккаунт уже зарегистрирована')
        if (len(email) != 0) and (check_unique(User, 'email', email) is False):
            raise forms.ValidationError('Эта почта уже зарегистрирована')
        self.cleaned_data['password'] = self.instance.password
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic_name', 'account_id', 'email')
    def clean_password2(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('last_name', 'first_name', 'patronymic_name', 'phone_number', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'patronymic_name')}),
        ('Contacts', {'fields': ('account_id', 'email')}),
        ('Permissions', {'fields': ('is_superuser','is_staff',)}),
    )
    # Superuser can be created only from tty
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'last_name', 'first_name', 'patronymic_name', 'account_id', 'email', 'is_staff', 'password1', 'password2')}
        ),
    )
    search_fields = ('last_name', 'phone_number', 'account_id', 'first_name', 'patronymic_name', 'email',)
    ordering = ('last_name', 'first_name', 'is_staff')
    filter_horizontal = ()

# Register the new UserAdmin
admin.site.register(User, UserAdmin)
# No permissions for now
admin.site.unregister(Group)

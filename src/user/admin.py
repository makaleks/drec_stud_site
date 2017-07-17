from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User

# Register your models here.

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label = 'Password confirmation', widget = forms.PasswordInput)
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic_name', 'account_url', 'email')
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
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic_name', 'account_url', 'email')
    def clean_password2(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserChangeForm
    list_display = ('last_name', 'first_name', 'patronymic_name', 'phone_number', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'patronymic_name')}),
        ('Contacts', {'fields': ('account_url', 'email')}),
        ('Permissions', {'fields': ('is_superuser','is_staff',)}),
    )
    # Superuser can be created only from tty
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'last_name', 'first_name', 'patronymic_name', 'account_url', 'email', 'is_staff',)}
        ),
    )
    search_fields = ('last_name', 'phone_number', 'account_url', 'first_name', 'patronymic_name', 'email',)
    ordering = ('last_name', 'first_name', 'is_staff',)
    filter_horizontal = ()

# Register the new UserAdmin
admin.site.register(User, UserAdmin)
# No permissions for now
admin.site.unregister(Group)

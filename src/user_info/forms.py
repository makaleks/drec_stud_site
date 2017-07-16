from django import forms
from .models import UserInfo
from django.contrib.auth.models import User

class UserForm(forms.ModelForm)
    class Meta:
        model = User
        firlds = ('first_name', 'last_name', 'email')

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ('pathronymic_name', 'phone_number')

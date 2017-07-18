from django.contrib.auth.models import BaseUserManager
from utils.validators import is_valid_name, is_valid_phone, is_valid_email


class UserManager(BaseUserManager):
    def create_user(self, last_name, first_name, patronymic_name, phone_number, account_url, email, password=None):
        if not first_name or not last_name or not patronymic_name or not phone_number:
            raise ValueError('Users must have first name, last name, patronymic name and phone number')
        if is_valid_name(first_name) is False:
            raise ValueError('First name format is incorrent')
        if is_valid_name(last_name) is False:
            raise ValueError('Last name format is incorrent')
        if is_valid_name(patronymic_name) is False:
            raise ValueError('Patronymic name format is incorrent')
        if is_valid_phone(phone_number) is False:
            raise ValueError('Phone format is incorrent')
        # 'email' is optional
        if (len(email) != 0) and (is_valid_email(email) is False):
            raise ValueError('Email format is incorrent')

        if check_unique(User, 'phone_number', phone_number) is False:
            raise forms.ValidationError('This phone number has been already registered')
        if check_unique(User, 'account_url', account_url) is False:
            raise forms.ValidationError('This account url has been already registered')
        if (len(email) != 0) and (check_unique(User, 'email', email) is False):
            raise forms.ValidationError('This email has been already registered')

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            phone_number = phone_number,
            account_url = account_url,
            password = password,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, last_name, first_name, patronymic_name, phone_number, account_url, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            phone_number = phone_number,
            password = password,
            account_url = account_url,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user

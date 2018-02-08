from django.contrib.auth.models import BaseUserManager
from utils.validators import *
from utils.utils import check_unique


class UserManager(BaseUserManager):
    # Replace next string with this one to enable #passwordAuth
    #def create_user(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, email, password=None):
    def create_user(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, account = 0, email = ''):
        if not first_name or not last_name or not patronymic_name or not phone_number:
            raise ValueError('Users must have first name, last name, patronymic name and phone number')
        if is_valid_name(first_name) is False:
            raise ValueError('First name format is incorrent')
        if is_valid_name(last_name) is False:
            raise ValueError('Last name format is incorrent')
        if is_valid_name(patronymic_name) is False:
            raise ValueError('Patronymic name format is incorrent')
        if is_valid_group(group_number) is False:
            raise ValueError('Group format is incorrent')
        if is_valid_phone(phone_number) is False:
            raise ValueError('Phone format is incorrent')
        # 'email' is optional
        if (len(email) != 0) and (is_valid_email(email) is False):
            raise ValueError('Email format is incorrent')

        if check_unique(self.model, 'account_id', account_id):
            raise ValueError('This account url has been already registered')
        if (len(email) != 0) and (check_unique(self.model, 'email', email)):
            raise ValueError('This email has been already registered')
        if (len(phone_number) != 0) and (check_unique(self.model, 'phone_number', phone_number)):
            raise ValueError('This phone number has been already registered')

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            group_number = group_number,
            phone_number = phone_number,
            account_id = account_id,
            account = account,
            # Uncomment to enable #passwordAuth
            #password = password,
        )
        # Uncomment to enable #passwordAuth
        #user.set_password(password)
        user.save(using = self._db)
        return user

    # Replace next string with this one to enable #passwordAuth
    #def create_superuser(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, email, password):
    def create_superuser(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, account = 0, email = ''):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            group_number = group_number,
            phone_number = phone_number,
            account_id = account_id,
            account = account
            # Uncomment to enable #passwordAuth
            #password = password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user

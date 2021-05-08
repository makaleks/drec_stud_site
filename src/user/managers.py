from django.contrib.auth.models import BaseUserManager
from utils.utils import check_unique


class UserManager(BaseUserManager):
    # Replace next string with this one to enable #passwordAuth
    def create_user(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, account = 0, email = '', password = None):
        # All validation is done by User model

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            group_number = group_number,
            phone_number = phone_number,
            account_id = account_id,
            account = account,
        )
        if password is None:
            password = self.make_random_password(length = 20)
        user.set_password(password)
        user.full_clean()
        user.save(using = self._db)
        return user

    # Replace next string with this one to enable #passwordAuth
    def create_superuser(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, password, account = 0, email = ''):
    #def create_superuser(self, last_name, first_name, patronymic_name, group_number, phone_number, account_id, account = 0, email = ''):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            patronymic_name = patronymic_name,
            group_number = group_number,
            phone_number = phone_number,
            account_id = account_id,
            account = account,
            password = password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user


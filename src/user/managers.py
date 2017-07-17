from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, last_name, first_name, patronymic_name, phone_number, account_url, email, password=None):
        if not first_name or not last_name or not patronymic_name or not phone_number:
            raise ValueError('Users must have first name, last name, patronymic name and phone number')
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

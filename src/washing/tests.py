# coding: utf-8
from django.test import TestCase
from django.core.files import File

from freezegun import freeze_time
import datetime

from user.models import User
from .models import Washing, WashingMachine, Order

# Create your tests here.

class WashingOrderingTestCase(TestCase):
    # Пошли как-то Петька и Василий Иванович стираться...
    def setUp(self):
        icon = open('washing/test_resources/icon_for_tests.png', 'rb')
        washing = Washing(name = 'Стиралка'.encode('utf-8'), image = File(icon), timestep = datetime.time(hour = 1))
        washing.save()
        WashingMachine.objects.bulk_create([
                WashingMachine(name = 'М1', service = washing),
                WashingMachine(name = 'М2', service = washing),
                WashingMachine(name = 'М3', service = washing),
                WashingMachine(name = 'М4', service = washing),
                WashingMachine(name = 'М5', service = washing),
            ])
        staff = User(first_name = 'Василий', patronymic_name = 'Иванович', last_name = 'Чапаев', account_id = '1', group_number = '311', account = 0, is_staff = True)
        staff.save()
        user = User(first_name = 'Петька', last_name = 'Хм', account_id = '3', account = 500, is_staff = False, group_number = '811')
        user.save()
        print('SetUp finished')
    def test1(self):
        pass


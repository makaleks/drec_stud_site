# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-02 06:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20171101_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='patronymic_name',
            field=models.CharField(default='', max_length=32, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default='', max_length=20, verbose_name='Контактный номер'),
        ),
    ]

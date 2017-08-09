# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-09 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('edited', models.DateTimeField(auto_now=True, verbose_name='Последнее редактирование')),
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'Заметка',
                'verbose_name_plural': 'Заметки',
                'ordering': ['name'],
            },
        ),
    ]

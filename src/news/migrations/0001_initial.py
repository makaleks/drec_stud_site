# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-28 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
                ('edited', models.DateTimeField(auto_now=True, verbose_name='Последнее редактирование')),
                ('title', models.CharField(max_length=64, verbose_name='Заголовок')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('image', models.ImageField(blank=True, upload_to='')),
            ],
        ),
    ]

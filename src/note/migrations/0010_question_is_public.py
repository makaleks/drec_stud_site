# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-06 14:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0009_auto_20171005_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Виден всем'),
        ),
    ]

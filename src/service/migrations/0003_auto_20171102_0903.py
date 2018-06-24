# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-02 06:03
from __future__ import unicode_literals

from django.db import migrations, models
import precise_bbcode.fields


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_auto_20170916_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='_instruction_rendered',
            field=models.TextField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='instruction',
            field=precise_bbcode.fields.BBCodeTextField(blank=True, no_rendered_field=True, null=True, verbose_name='Инструкция и подробное описание'),
        ),
    ]

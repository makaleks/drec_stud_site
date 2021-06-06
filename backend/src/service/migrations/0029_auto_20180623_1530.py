# Generated by Django 2.0 on 2018-06-23 15:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0028_auto_20180623_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='late_cancel_multiplicator',
            field=models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='На сколько умножить при поздней отмене'),
        ),
    ]
# Generated by Django 2.0 on 2018-04-07 20:50

import django.core.validators
from django.db import migrations
import utils.model_aliases


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0023_auto_20180407_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='image',
            field=utils.model_aliases.DefaultImageField(upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'svg'])], verbose_name='Изображение (jpg, jpeg, png, gif, svg)'),
        ),
    ]

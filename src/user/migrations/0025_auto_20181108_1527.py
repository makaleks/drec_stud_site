# Generated by Django 2.1.1 on 2018-11-08 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_faculty'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='room_number',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Номер комнаты'),
        ),
        migrations.AlterField(
            model_name='user',
            name='group_number',
            field=models.CharField(max_length=7, verbose_name='Номер группы'),
        ),
    ]

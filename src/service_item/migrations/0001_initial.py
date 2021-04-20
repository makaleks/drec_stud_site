# Generated by Django 2.1.1 on 2018-09-30 22:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkingTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.PositiveSmallIntegerField(choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье'), (8, 'Ежедневно')], default=8, verbose_name='Рабочее время')),
                ('works_from', models.TimeField(default=datetime.time(0, 0), verbose_name='Начало рабочего времени (включительно)')),
                ('works_to', models.TimeField(default=datetime.time(0, 0), verbose_name='Конец рабочего времени (не включительно)')),
                ('is_weekend', models.BooleanField(default=False, verbose_name='Выходной')),
                ('description', models.CharField(blank=True, max_length=64, null=True, verbose_name='Описание')),
                ('object_id', models.PositiveIntegerField(verbose_name='Id назначения')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Тип назначения')),
            ],
            options={
                'verbose_name': 'Время работы',
                'verbose_name_plural': 'Расписания',
                'ordering': ['object_id', 'weekday', 'works_from', 'works_to'],
            },
        ),
        migrations.CreateModel(
            name='WorkingTimeException',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(default=datetime.date.today, verbose_name='День начала (включительно)')),
                ('date_end', models.DateField(default=datetime.date.today, verbose_name='День окончания (включительно)')),
                ('works_from', models.TimeField(default=datetime.time(0, 0), verbose_name='Начало рабочего времени (включительно)')),
                ('works_to', models.TimeField(default=datetime.time(0, 0), verbose_name='Конец рабочего времени (не включительно)')),
                ('is_weekend', models.BooleanField(default=False, verbose_name='Выходной')),
                ('is_annual', models.BooleanField(default=False, verbose_name='Ежегодно')),
                ('description', models.CharField(blank=True, max_length=64, null=True, verbose_name='Описание')),
                ('object_id', models.PositiveIntegerField(verbose_name='Id назначения')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Тип назначения')),
            ],
            options={
                'verbose_name': 'Дата исключения',
                'verbose_name_plural': 'Даты исключений',
                'ordering': ['object_id', 'is_annual', 'date_start', 'date_end', 'works_from'],
            },
        ),
    ]
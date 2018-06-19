# Generated by Django 2.0 on 2018-04-09 14:02

from django.db import migrations, models
import precise_bbcode.fields


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0004_comment_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='_text_rendered',
            field=models.TextField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=precise_bbcode.fields.BBCodeTextField(no_rendered_field=True, verbose_name='Текст'),
        ),
    ]
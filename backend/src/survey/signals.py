from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.files import File
from openpyxl import Workbook
import os

from .models import AnswerData

@receiver(post_save, sender=AnswerData)
def gen_sheet(sender, instance, **kwargs):
    wb = instance.survey.gen_sheet()
    tmp_path = os.path.join('/tmp/', 'survey_for_{0}.xlsx'.format(instance.survey.id))
    wb.save(tmp_path)
    saved = open(tmp_path, 'rb')
    django_file = File(saved)
    instance.survey.sheet.save('survey_for_{0}.xlsx'.format(instance.survey.id), django_file, save = True)
    saved.close()


from django.contrib import admin
from utils.custom_admins import CustomBaseAdmin
from reversion.admin import VersionAdmin
from .models import Survey, Answer, AnswerData

# Register your models here.

@admin.register(Survey)
class SurveyAdmin(CustomBaseAdmin, VersionAdmin):
    list_display = ('title', 'id_link', 'started', 'finished')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['is_anonymous', 'sheet']
        else:
            return []
    def get_exclude(self, request, obj=None):
        if not obj:
            return ['sheet']
        else:
            return []

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created')

@admin.register(AnswerData)
class AnswerDataAdmin(admin.ModelAdmin):
    list_display = ('pk', 'answer')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['value']
        else:
            return []

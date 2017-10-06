from django.contrib import admin
from .models import Survey, Answer

# Register your models here.

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'started', 'finished')

@admin.register(Answer)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('survey', 'user', 'created')

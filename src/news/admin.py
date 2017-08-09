from django.contrib import admin
from .models import News

# Register your models here.

# Use __unicode__() on model to show only title
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'edited', 'created')

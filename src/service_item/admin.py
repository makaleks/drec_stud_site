from django.contrib import admin

from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import WorkingTime, WorkingTimeException

# Register your models here.

@admin.register(WorkingTime)
class WorkingTimeAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('weekday', 'is_weekend', 'works_from', 'works_to')
    ordering = ['weekday', 'is_weekend', 'works_from', 'works_to']

@admin.register(WorkingTimeException)
class WorkingTimeExceptionAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('date_start', 'date_end', 'is_weekend', 'works_from', 'works_to')
    ordering = ['is_annual', 'date_start', 'date_end', 'is_weekend', 'works_from', 'works_to']


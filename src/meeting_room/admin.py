from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import MeetingRoom, MeetingRoomItem, Order
from service_item.models import WorkingTime, WorkingTimeException

# Register your models here.

class WorkingTimeInline(GenericStackedInline):
    model = WorkingTime
    extra = 0
    verbose_name = 'Элемент'
    ordering = ['weekday', 'works_from', 'works_to']

class WorkingTimeExceptionInline(GenericStackedInline):
    model = WorkingTimeException
    extra = 0
    verbose_name = 'Элемент'
    ordering = ['is_annual', 'date_start', 'date_end', 'works_from', 'works_to']

@admin.register(MeetingRoom)
class MeetingRoomAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    inlines = [WorkingTimeInline, WorkingTimeExceptionInline]
    list_filter = ['order', 'name']
    list_display = ('name', 'timestep', 'is_active','edited')

@admin.register(Order)
class OrderAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'item', 'is_approved', 'is_good', 'user_info', 'item_id', 'date_start', 'time_start', 'time_end')
    list_filter = ['date_start', 'item_id']
    ordering = ('is_approved', '-date_start', 'item', 'time_start', 'user')
    def user_info(self, obj):
        return '{0}, {1}'.format(obj.user.group_number, obj.user.get_full_name())
    def item_id(self, obj):
        return obj.item.id
    def is_good(self, obj):
        return obj.is_good()
    is_good.short_description = 'Не поздно'


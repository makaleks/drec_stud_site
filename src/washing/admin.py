from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import Washing, WashingMachine, Order
from service_item.models import WorkingTime, WorkingTimeException

# Register your models here.

class WashingMachineInline(SortableInlineAdminMixin, admin.TabularInline):
#class WashingMachineInline(admin.TabularInline, SortableInlineAdminMixin):
    model = WashingMachine
    extra = 0
    verbose_name = 'Машинка'
    ordering = ['order', 'price']

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

@admin.register(Washing)
class WashingAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    inlines = [WashingMachineInline, WorkingTimeInline, WorkingTimeExceptionInline]
    list_filter = ['order', 'name']
    list_display = ('name', 'default_price', 'timestep', 'is_active','edited')

@admin.register(WashingMachine)
class WashingMachineAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'name', 'is_active', 'created')
    list_filter = ['order', 'is_active']
    inlines = [WorkingTimeInline, WorkingTimeExceptionInline]

@admin.register(Order)
class OrderAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'item', 'user_info', 'item_id', 'date_start', 'time_start', 'time_end')
    list_filter = ['date_start', 'item_id']
    ordering = ('-date_start', 'item', 'time_start', 'user')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('payed', 'used')
        else:
            return ('payed',)
    def user_info(self, obj):
        return '{0}, {1}'.format(obj.user.group_number, obj.user.get_full_name())
    def item_id(self, obj):
        return obj.item.id


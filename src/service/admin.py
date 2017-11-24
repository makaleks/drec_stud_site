from django.contrib import admin
from .models import WorkingTime, WorkingTimeException, Service, Item, Order
from django.contrib.contenttypes.admin import GenericStackedInline
from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin
from django import forms

# Register your models here.

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    verbose_name = 'Элемент'
    ordering = ['location', 'price']

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

@admin.register(WorkingTime)
class WorkingTimeAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'works_from', 'works_to')
    ordering = ['weekday', 'works_from', 'works_to']

@admin.register(WorkingTimeException)
class WorkingTimeExceptionAdmin(admin.ModelAdmin):
    list_display = ('date_start', 'date_end', 'works_from', 'works_to')
    ordering = ['is_annual', 'date_start', 'date_end', 'works_from', 'works_to']

@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, VersionAdmin):
    list_display = ('slug', 'default_price', 'time_step', 'is_active','edited')
    inlines = [ItemInline, WorkingTimeInline, WorkingTimeExceptionInline]
    list_filter = ['name']
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['slug']
        else:
            return []

@admin.register(Item)
class ItemAdmin(SortableAdminMixin, VersionAdmin):
    list_display = ('id', 'name', 'is_active', 'created')
    list_filter = ['location', 'is_active']
    inlines = [WorkingTimeInline, WorkingTimeExceptionInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_info', 'item_id', 'date_start', 'time_start', 'time_end')
    list_filter = ['date_start', 'item_id']
    def user_info(self, obj):
        return '{0}, {1}'.format(obj.user.group_number, obj.user.get_full_name())
    def item_id(self, obj):
        return obj.item.id

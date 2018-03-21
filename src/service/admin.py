from django.contrib import admin
from .models import WorkingTime, WorkingTimeException, Service, Item, Order,Participation
from django.contrib.contenttypes.admin import GenericStackedInline
from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django import forms
from django.http import QueryDict

# Register your models here.

class ItemInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Item
    extra = 0
    verbose_name = 'Элемент'
    ordering = ['order', 'location', 'price']

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
class WorkingTimeAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('weekday', 'is_weekend', 'works_from', 'works_to')
    ordering = ['weekday', 'is_weekend', 'works_from', 'works_to']

@admin.register(WorkingTimeException)
class WorkingTimeExceptionAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('date_start', 'date_end', 'is_weekend', 'works_from', 'works_to')
    ordering = ['is_annual', 'date_start', 'date_end', 'is_weekend', 'works_from', 'works_to']

class ServiceForm(forms.ModelForm):
    def clean(self):
        # 'self' was used in official tutorial in User override
        self.cleaned_data = super(ServiceForm, self).clean()
        #if self.cleaned_data['default_works_to'] < self.cleaned_data['default_works_from']:
        #    raise forms.ValidationError('Пожалуйста, установите время работы в пределах 1 дня')
        if self.cleaned_data['is_single_item']:
            got_item_forms_count =int(self.data.get('items-TOTAL_FORMS', 0))
            to_delete_item_count = 0
            cursor = 0
            for i in range(0, got_item_forms_count):
                if self.data.get('items-{0}-DELETE'.format(i), '') == 'on':
                    to_delete_item_count += 1
                else:
                    cursor = i
            if got_item_forms_count - to_delete_item_count != 1:
                raise forms.ValidationError('Если установлено \'один предмет сервиса\', то их количество должно быть равно 1')
        return self.cleaned_data
    class Meta:
        model = Service
        # error fix: "Creating a ModelForm without either the 'fields' attribute or the 'exclude' attribute is prohibited"
        exclude = []

@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    form = ServiceForm
    list_display = ('name', 'default_price', 'timestep', 'is_active','edited')
    inlines = [ItemInline, WorkingTimeInline, WorkingTimeExceptionInline]
    list_filter = ['order', 'name']
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['slug']
        else:
            return []
    #def get_inline_instances(self, request, obj=None):
    #    if obj and obj.is_single_item:
    #        return []
    #    else:
    #        return super(ServiceAdmin, self).get_inline_instances(request, obj)

@admin.register(Item)
class ItemAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'name', 'is_active', 'created')
    list_filter = ['order', 'location', 'is_active']
    inlines = [WorkingTimeInline, WorkingTimeExceptionInline]

@admin.register(Order)
class OrderAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'item', 'user_info', 'item_id', 'is_approved', 'date_start', 'time_start', 'time_end')
    list_filter = ['date_start', 'item_id']
    def user_info(self, obj):
        return '{0}, {1}'.format(obj.user.group_number, obj.user.get_full_name())
    def item_id(self, obj):
        return obj.item.id

@admin.register(Participation)
class ParticipationAdmin(VersionAdmin):
    history_latest_first = True
    list_display = ('order', 'user')

from django.contrib import admin

from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin

from .models import MenuEntry

# Register your models here.

@admin.register(MenuEntry)
class MenuEntryAdmin(SortableAdminMixin, VersionAdmin):
    history_latest_first = True
    list_display = ('id', 'name', 'url')


from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Note

# Register your models here.

@admin.register(Note)
class NoteAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'edited')

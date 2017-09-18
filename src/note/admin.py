from django.contrib import admin
from .models import Note

# Register your models here.

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('name', 'edited')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name']
        else:
            return []

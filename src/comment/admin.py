from django.contrib import admin
from .models import Comment

# Register your models here.

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'first_text', 'object_type', 'object_id', 'edited', 'created']

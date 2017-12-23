from django.contrib import admin
from reversion.admin import VersionAdmin
from adminsortable2.admin import SortableAdminMixin
from .models import Note, Question

import logging
logger = logging.getLogger('site_events')

# Register your models here.

class NoteAdmin(SortableAdminMixin, VersionAdmin):
    list_display = ('name', 'edited')
    def save_model(self, request, obj, form, change):
        if change:
            fields = [{field: str(getattr(obj, field))} for field in form.changed_data]
            logger.info('{0} \'{1}\' was {2}'.format(self.model.__name__, str(obj), 'edited in {0}'.format(str(fields)) if fields else 'just saved'), extra={'user': request.user.get_full_name()})
        else:
            fields = [{f.name: str(getattr(obj, f.name))} for f in obj._meta.fields]
            logger.info('{0} \'{1}\' was created as {2}'.format(self.model.__name__, str(obj), str(fields)), extra={'user': request.user.get_full_name()})
        super(NoteAdmin, self).save_model(request, obj, form, change)
    def delete_model(self, request, obj):
        logger.info('{0} \'{1}\' was deleted'.format(self.model.__name__, str(obj)), extra={'user': request.user.get_full_name()})
        super(NoteAdmin, self).delete_model(request, obj)
admin.site.register(Note, NoteAdmin)


class QuestionAdmin(VersionAdmin):
    list_display = ('author', 'title', 'is_approved', 'edited', 'created')
    def save_model(self, request, obj, form, change):
        if change:
            fields = [{field: str(getattr(obj, field))} for field in form.changed_data]
            logger.info('{0} \'{1}\' was {2}'.format(self.model.__name__, str(obj), 'edited in {0}'.format(str(fields)) if fields else 'just saved'), extra={'user': request.user.get_full_name()})
        else:
            fields = [{f.name: str(getattr(obj, f.name))} for f in obj._meta.fields]
            logger.info('{0} \'{1}\' was created as {2}'.format(self.model.__name__, str(obj), str(fields)), extra={'user': request.user.get_full_name()})
        super(QuestionAdmin, self).save_model(request, obj, form, change)
    def delete_model(self, request, obj):
        logger.info('{0} \'{1}\' was deleted'.format(self.model.__title__, str(obj)), extra={'user': request.user.get_full_name()})
        super(QuestionAdmin, self).delete_model(request, obj)
admin.site.register(Question, QuestionAdmin)

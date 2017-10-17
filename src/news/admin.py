from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import News

import logging
logger = logging.getLogger('site_events')

# Register your models here.

class NewsAdmin(VersionAdmin):
    list_display = ('title', 'id', 'edited', 'created')
    history_latest_first = True
    def save_model(self, request, obj, form, change):
        if change:
            fields = [{field: str(getattr(obj, field))} for field in form.changed_data]
            logger.info('{0} \'{1}\' was {2}'.format(self.model.__name__, str(obj), 'edited in {0}'.format(str(fields)) if fields else 'just saved'), extra={'user': request.user.get_full_name()})
        else:
            fields = [{f.name: str(getattr(obj, f.name))} for f in obj._meta.fields]
            logger.info('{0} \'{1}\' was created as {2}'.format(self.model.__name__, str(obj), str(fields)), extra={'user': request.user.get_full_name()})
        super(NewsAdmin, self).save_model(request, obj, form, change)
    def delete_model(self, request, obj):
        logger.info('{0} \'{1}\' was deleted'.format(self.model.__name__, str(obj)), extra={'user': request.user.get_full_name()})
        super(NewsAdmin, self).delete_model(request, obj)
# Decorators create a subclass, so 'super' does not work
admin.site.register(News, NewsAdmin)

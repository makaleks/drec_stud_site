from django.conf.urls import url
from .views import unlock, list_update

urlpatterns = [
    url(r'^(?P<service_name>.+)/list-update$', list_update),
    url(r'^(?P<service_name>.+)/$', unlock),
]

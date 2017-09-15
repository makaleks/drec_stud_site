from django.conf.urls import url
from .views import unlock, list_update, ServiceListView, ServiceDetailView

urlpatterns = [
    url(r'^(?P<service_name>.+)/list-update/$', list_update),
    url(r'^(?P<service_name>.+)/unlock/$', unlock),
    url(r'^(?P<slug>.+)/$', ServiceDetailView.as_view(), name = 'service'),
    url(r'^$', ServiceListView.as_view()),
]

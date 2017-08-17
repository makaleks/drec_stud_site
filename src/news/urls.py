from django.conf.urls import url, include
from .views import NewsListView, archive_draw, archive_process

urlpatterns = [
    url(r'^$', NewsListView.as_view(), name = 'news'),
    url(r'^archive/$', archive_draw),
    url(r'^archive_get/$', archive_process),
]

from django.urls import path
from .views import NewsListView, archive_draw, archive_get

app_name = 'news'
urlpatterns = [
    path('',             NewsListView.as_view(), name = 'news-list'),
    path('archive/',     archive_draw, name = 'news-archive'),
    path('archive_get/', archive_get),
]

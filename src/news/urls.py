from django.conf.urls import url, include
from .views import NewsListView

urlpatterns = [
    url(r'^$', NewsListView.as_view(), name = 'news_list'),
]

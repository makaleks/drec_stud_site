from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', PostList.as_view(), name="post_list"),
]

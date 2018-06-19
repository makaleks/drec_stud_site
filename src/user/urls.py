from django.urls import path, include
from .views import UserUidSetView

app_name = 'user'
urlpatterns = [
    path('uid', UserUidSetView.as_view(), name = 'uid_set'),
]

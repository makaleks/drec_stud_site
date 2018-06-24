from django.urls import path, include
from .views import UserUidSetView, long_logout

app_name = 'user'
urlpatterns = [
    path('uid', UserUidSetView.as_view(), name = 'uid_set'),
    path('long-logout', long_logout),
]

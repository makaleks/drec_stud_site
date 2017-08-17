from django.conf.urls import url, include
from .views import NoteDetailView

urlpatterns = [
    url(r'^(?P<pk>.+)/$', NoteDetailView.as_view(), name = 'note'),
]

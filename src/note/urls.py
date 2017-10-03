from django.conf.urls import url, include
from .views import NoteFormListView

urlpatterns = [
    url(r'$', NoteFormListView.as_view(), name = 'note_list'),
]

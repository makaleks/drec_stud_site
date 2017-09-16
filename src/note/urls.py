from django.conf.urls import url, include
from .views import NoteListView

urlpatterns = [
    url(r'$', NoteListView.as_view(), name = 'note_list'),
]

from django.conf.urls import url, include
from .views import NoteFormListView, QuestionDetailView, NoteDetailView

urlpatterns = [
    url(r'^$', NoteFormListView.as_view(), name = 'note_list'),
    url(r'^(?P<pk>\d+)/$', QuestionDetailView.as_view(), name = 'question_detail'),
    url(r'^(?P<slug>.+)/$', NoteDetailView.as_view(), name = 'note_detail'),
]

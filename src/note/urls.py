from django.conf.urls import url, include
from .views import NoteFormListView, QuestionDetailView

urlpatterns = [
    url(r'^$', NoteFormListView.as_view(), name = 'note_list'),
    url(r'^(?P<pk>\d+)/$', QuestionDetailView.as_view(), name = 'question_detail'),
]

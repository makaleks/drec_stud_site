from django.conf.urls import url, include
from .views import NoteListView, StudentCouncilView, QuestionDetailView, NoteDetailView

urlpatterns = [
    url(r'^student_council/$', StudentCouncilView.as_view(), name = 'council'),
    url(r'^$', NoteListView.as_view(), name = 'note_list'),
    url(r'^student_council/(?P<pk>\d+)/$', QuestionDetailView.as_view(), name = 'question_detail'),
    url(r'^(?P<slug>.+)/$', NoteDetailView.as_view(), name = 'note_detail'),
]

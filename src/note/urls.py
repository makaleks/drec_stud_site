from django.urls import path, include
from .views import NoteListView, StudentCouncilView, QuestionDetailView, NoteDetailView

# Use 'name=' for reverse view resolution of URL
# 'namespace=' is a namespace for 'name='

app_name = 'note'
urlpatterns = [
    path('student_council/<int:pk>/', QuestionDetailView.as_view(), name = 'question-detail'),
    path('student_council/', StudentCouncilView.as_view(), name = 'student-council'),
    path('<int:pk>/',        NoteDetailView.as_view(), name = 'note-id-detail'),
    path('<slug:slug>/',     NoteDetailView.as_view(), name = 'note-slug-detail'),
    path('',                 NoteListView.as_view(), name = 'note-base'),
]

from django.urls import path, include
from .views import SurveyListView, SurveyDetailView
from django.views.generic.base import TemplateView

app_name = 'survey'
urlpatterns = [
    path('',         SurveyListView.as_view(), name = 'survey_list'),
    path('<int:pk>', SurveyDetailView.as_view(), name = 'survey_detail'),
    path('test',     TemplateView.as_view(template_name = 'chart.html')),
]

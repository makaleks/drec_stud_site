from django.conf.urls import url, include
from .views import SurveyCreateView, SurveyListView, SurveyDetailView, SurveyUpdateView

urlpatterns = [
    url(r'^create/$', SurveyCreateView.as_view(), name = 'survey_create'),
    url(r'^$', SurveyListView.as_view(), name = 'survey_list'),
    url(r'^(?P<pk>\d+)/$', SurveyDetailView.as_view(), name = 'survey_detail'),
    url(r'^(?P<pk>\d+)/edit/$', SurveyUpdateView.as_view(), name = 'survey_edit'),
]

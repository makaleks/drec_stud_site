from django.conf.urls import url, include
from .views import SurveyListView, SurveyDetailView

urlpatterns = [
    url(r'^$', SurveyListView.as_view(), name = 'survey_list'),
    url(r'^(?P<pk>\d+)/$', SurveyDetailView.as_view(), name = 'survey_detail'),
]

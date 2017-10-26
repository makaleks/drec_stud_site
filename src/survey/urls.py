from django.conf.urls import url, include
from .views import SurveyListView, SurveyDetailView
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', SurveyListView.as_view(), name = 'survey_list'),
    url(r'^(?P<pk>\d+)/$', SurveyDetailView.as_view(), name = 'survey_detail'),
    url(r'^test$', TemplateView.as_view(template_name = 'chart.html')),
]

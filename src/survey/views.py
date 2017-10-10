from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Q
from .models import Survey, Answer

import datetime

# Create your views here.

class SurveyListView(TemplateView):
    template_name = 'survey_list.html'
    # get for last month
    def get_context_data(self, **kwargs):
        context = super(SurveyListView, self).get_context_data(**kwargs)
        now = datetime.datetime.now()
        #years = self.request.GET.get('years')
        #if years:
        #    queryset = queryset.filter(Q(started__year__in = years.split('-')) | Q(started__year__in = years.split('-'))).order_by('-started')
        queryset = Survey.objects.all()
        queyset_now = queryset.filter(Q(started__lte = now) & Q(finished__gt = now))
        queryset_finished = queryset.filter(finished__lt = now)
        context['survey_list_now'] = list(queyset_now)
        context['survey_list_finished'] = list(queryset_finished)
        return context

class SurveyDetailView(DetailView):
    model = Survey
    template_name = 'survey_detail.html'
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        data = request.POST.dict()
        rewrite = False
        finished = False
        started = True
        queryset = Answer.objects.all().filter(survey = Survey.objects.all().filter(pk = data['survey_pk']).first(), user = request.user)
        if queryset.exists():
            a = queryset.first()
            rewrite = True
            a.answer = data['survey_result']
        else:
            a = Answer(answer = data['survey_result'], survey = Survey.objects.all().filter(pk = data['survey_pk']).first(), user = request.user)
        if a.survey.finished < datetime.datetime.now():
            finished = True
        elif a.survey.started > datetime.datetime.now():
            started = False
        else:
            a.save()
        return render(request, 'survey_thanks.html', {'rewrite': rewrite, 'finished': finished, 'started': started})


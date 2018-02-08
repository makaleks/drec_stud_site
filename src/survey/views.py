from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from .models import Survey, Answer, AnswerData

# Create your views here.

class SurveyListView(TemplateView):
    template_name = 'survey_list.html'
    # get for last month
    def get_context_data(self, **kwargs):
        context = super(SurveyListView, self).get_context_data(**kwargs)
        now = timezone.now()
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
        status = 'created'
        finished = False
        started = True
        survey = Survey.objects.all().filter(pk = data['survey_pk']).first()
        queryset = Answer.objects.all().filter(survey = survey, user = request.user)
        a_data = None
        if queryset.exists():
            a = queryset.first()
            if survey.allow_rewrite:
                status = 'edited'
                a_data = a.answer_data.first()
                a_data.value = data['survey_result']
                if not survey.is_anonymous:
                    a_data.answer = a
            else:
                status = 'noedit'
        else:
            a = Answer(survey = Survey.objects.all().filter(pk = data['survey_pk']).first(), user = request.user)
            a_data = AnswerData(value = data['survey_result'])
            a_data.survey = survey
        if a.survey.finished < timezone.now():
            finished = True
        elif a.survey.started > timezone.now():
            started = False
        else:
            with transaction.atomic():
                a.save()
                if a_data:
                    # querysets are lazy!
                    if not survey.is_anonymous and queryset.exists():
                        queryset = Answer.objects.all().filter(survey = survey, user = request.user)
                        a_data.answer = queryset.first()
                    a_data.save()
        return render(request, 'survey_thanks.html', {'status': status, 'finished': finished, 'started': started})


from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from .models import Survey
from .forms import SurveyCreateForm, SurveyUpdateForm

# Create your views here.

class SurveyListView(ListView):
    model = Survey
    template_name = 'survey_list.html'
    # get for last month
    def get_queryset(self):
        queryset = Survey.objects.all()
        years = self.request.GET.get('years')
        if years:
            queryset = queryset.filter(Q(started__year__in = years.split('-')) | Q(started__year__in = years.split('-'))).order_by('-started')
        return queryset

class SurveyCreateView(CreateView):
    model = Survey
    form_class = SurveyCreateForm
    template_name = 'survey_edit.html'
    def get_success_url(self):
        return reverse('survey_edit', args=(self.object.pk,))
    def get_context_data(self, **kwargs):
        context = super(SurveyCreateView, self).get_context_data(**kwargs)
        context['created'] = False
        return context

class SurveyUpdateView(UpdateView):
    model = Survey
    form_class = SurveyUpdateForm
    template_name = 'survey_edit.html'
    def get_success_url(self):
        return reverse('survey_edit', args=(self.object.pk,))
    def get_context_data(self, **kwargs):
        context = super(SurveyUpdateView, self).get_context_data(**kwargs)
        context['created'] = True
        return context

class SurveyDetailView(DetailView):
    model = Survey
    template_name = 'survey_detail.html'

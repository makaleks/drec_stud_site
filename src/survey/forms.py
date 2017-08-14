# coding: utf-8
from django import forms
from .models import Survey

class SurveyCreateForm(forms.ModelForm):
    structure   = forms.CharField(widget = forms.HiddenInput());
    class Meta:
        model = Survey
        fields = ['title', 'description', 'structure']

class SurveyUpdateForm(forms.ModelForm):
    structure   = forms.CharField(widget = forms.HiddenInput());
    class Meta:
        model = Survey
        fields = ['title', 'description', 'started', 'finished', 'structure']

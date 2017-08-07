from django import forms
from .models import News

def get_choices():
    return [[-1, 'Все']] + [[d.year, str(d.year)] for d in list(News.objects.all().dates('created', 'year', order = 'DESC'))]

class ArchiveSelectForm(forms.Form):
    vals = forms.MultipleChoiceField(
        choices = get_choices, 
        widget=forms.CheckboxSelectMultiple,
        label = 'Выбрать по годам'
    )

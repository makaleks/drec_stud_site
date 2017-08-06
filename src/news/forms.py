from django import forms
from .models import News

class ArchiveSelectForm(forms.Form):
    vals = forms.MultipleChoiceField(
        choices = [[-1, 'Все']] + [[d.year, str(d.year)] for d in list(News.objects.all().dates('created', 'year', order = 'DESC'))], 
        widget=forms.CheckboxSelectMultiple,
        label = 'Выбрать по годам'
    )

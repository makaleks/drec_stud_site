from django import forms
from .models import News

# If you insert this content directly in MultipleChoiceField,
# you will get error at './manage.py migrate', because
# model 'News' does not exists.
# So this function saves us :)
def get_choices():
    return [[-1, 'Все']] + [[d.year, str(d.year)] for d in list(News.objects.all().dates('created', 'year', order = 'DESC'))]

class ArchiveSelectForm(forms.Form):
    vals = forms.MultipleChoiceField(
        choices = get_choices, 
        widget=forms.CheckboxSelectMultiple,
        label = 'Выбрать по годам'
    )

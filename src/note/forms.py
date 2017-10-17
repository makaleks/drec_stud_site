# coding: utf-8
from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    check_to_send = forms.BooleanField(error_messages={'data-pattern-error':'heh'})
    def clean_title(self):
        title = self.cleaned_data['title']
        some = Question.objects.all().filter(title = title)
        if some.exists():
            raise forms.ValidationError('Заголовок занят!')
        return title
    class Meta:
        model = Question
        exclude = ('author',)
        error_messages = {
            'title': {
                'required': 'Не забудьте дать уникальный заголовок вопросу, чтобы не потерять его среди прочих : )',
            },
            'text': {
                'required': 'Не забудьте записать то, ради чего вы создавали опрос : )',
            },
            'check_to_send': {
                'required': 'Вы же проверили, да? : )',
            },
        }

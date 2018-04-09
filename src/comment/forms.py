# coding: utf-8
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    check_to_send = forms.BooleanField(error_messages={'data-pattern-error':'heh'})
    answerto = forms.CharField(error_messages={'data-pattern-error':'heh'}, widget=forms.TextInput(attrs={'id': 'answerto', 'name':'answerto', 'class': 'hidden'}), required=False)
    class Meta:
        model = Comment
        exclude = ('author','commented_object', 'object_type', 'object_id')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }

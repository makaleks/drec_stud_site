from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.http import HttpResponseBadRequest
from .models import Note, Question
from .forms import QuestionForm

# Create your views here.

class NoteFormListView(FormView):
    model = Note
    template_name = 'note_list.html'
    form_class = QuestionForm
    success_url = ''
    def get_context_data(self, **kwargs):
        context = super(NoteFormListView, self).get_context_data(**kwargs)
        context['note_list'] = Note.objects.all()
        context['question_list'] = Question.objects.all()
        return context
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(NoteListView, self).form_valid(form)

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'question.html'

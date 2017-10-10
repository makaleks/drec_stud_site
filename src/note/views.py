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
    success_url = '/notes/'
    def get_context_data(self, **kwargs):
        context = super(NoteFormListView, self).get_context_data(**kwargs)
        context['note_list'] = Note.objects.all()
        context['question_list'] = Question.objects.all()
        return context
    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            form.add_error(None, 'Сначала нужно войти на сайт!')
            return self.form_invalid(form)
        else:
            form.instance.author = self.request.user
        form.save()
        return super(NoteFormListView, self).form_valid(form)

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'question.html'

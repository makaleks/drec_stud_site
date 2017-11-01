from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponseBadRequest
from .models import Note, Question
from .forms import QuestionForm
from django.views.generic.detail import DetailView


# Create your views here.

class NoteListView(ListView):
    model = Note
    template_name = 'note_list.html'
    def get_queryset(self, **kwargs):
        return Note.objects.all().exclude(slug = 'student_council')

class StudentCouncilView(FormView):
    model = Note
    template_name = 'student_council.html'
    form_class = QuestionForm
    success_url = '/notes/student_council'
    def get_context_data(self, **kwargs):
        context = super(StudentCouncilView, self).get_context_data(**kwargs)
        context['note'] = Note.objects.all().filter(slug = 'student_council').first()
        context['question_list'] = Question.objects.all()
        return context
    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            form.add_error(None, 'Сначала нужно войти на сайт!')
            return self.form_invalid(form)
        else:
            form.instance.author = self.request.user
        form.save()
        return super(StudentCouncilView, self).form_valid(form)

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'question.html'

class NoteDetailView(DetailView):
    model = Note
    template_name = 'note_detail.html'

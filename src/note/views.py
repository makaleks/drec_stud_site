from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from .models import Note, Question
from .forms import QuestionForm
from django.views.generic.detail import DetailView
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment


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
    template_name = 'qanda.html'
    status = ''
    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        if request.user.is_authenticated:
            text = data['text']
            object_id = data['answerto']
            question = self.get_object()
            # Comment or edit existing
            if object_id:
                comment = Comment.objects.all().filter(id = object_id)
                if not comment.exists() or comment.first().author != request.user:
                    comment = Comment(author = request.user, text = text)
                    comment.object_type = ContentType.objects.get(app_label='comment', model = 'comment')
                    comment.object_id = object_id
                else:
                    comment = comment.first()
                    comment.text = text
            # Comment the Question
            else:
                comment = Comment(author = request.user, text = text)
                comment.object_type = ContentType.objects.get(app_label = 'note', model = 'question')
                comment.object_id = question.id
                comment.text = text
            comment.save()
        return HttpResponseRedirect('')

class NoteDetailView(DetailView):
    model = Note
    template_name = 'note_detail.html'

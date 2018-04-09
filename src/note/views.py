from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .models import Note, Question
from .forms import QuestionForm
from comment.forms import CommentForm
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from comment.models import Comment

import json


# Create your views here.

class NoteListView(ListView):
    model = Note
    template_name = 'note_list.html'
    # For Notes get_absolute_url (see models.py)
    tab = {}
    def get_queryset(self, **kwargs):
        return Note.objects.all().exclude(slug = 'student_council')
    def get_context_data(self, **kwargs):
        context = super(NoteListView, self).get_context_data(**kwargs)
        context['tab'] = self.tab
        return context
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        # For Notes get_absolute_url (see models.py)
        tab = data.get('tab')
        if tab:
            self.tab[tab] = True
        return super(NoteListView, self).get(request, *args, **kwargs)

class StudentCouncilView(FormView):
    model = Note
    template_name = 'student_council.html'
    form_class = QuestionForm
    success_url = '/notes/student_council?status=success'
    status = ''
    # used to save navigation position
    # missed keys are interpreted as 'False'
    tab = {}
    def get_context_data(self, **kwargs):
        context = super(StudentCouncilView, self).get_context_data(**kwargs)
        context['note'] = Note.objects.all().filter(slug = 'student_council').first()
        context['question_list'] = Question.objects.all()
        modal = {}
        if self.status:
            status = self.status
            if status == 'success' and not settings.QUESTION_DEFAULT_APPROVED:
                modal['text'] = 'Вопрос отправлен и скоро, после одобрения, будет опубликован'
                modal['enabled'] = True
                modal['type'] = self.status
        context['notification'] = modal
        context['tab'] = self.tab
        return context
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        status = data.get('status')
        if status:
            self.status = status
        return super(StudentCouncilView, self).get(request, *args, **kwargs)
    def form_valid(self, form):
        self.tab['new_question'] = True
        if not self.request.user.is_authenticated:
            form.add_error(None, 'Сначала нужно войти на сайт!')
            return self.form_invalid(form)
        else:
            form.instance.author = self.request.user
        form.save()
        return super(StudentCouncilView, self).form_valid(form)
    def form_invalid(self, form):
        self.tab['new_question'] = True
        return super(StudentCouncilView, self).form_invalid(form)

class QuestionDetailView(FormMixin, DetailView):
    model = Question
    form_class = CommentForm
    template_name = 'qanda.html'
    def get_success_url(self):
        return reverse('note:question-detail', kwargs={'pk': self.object.pk})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        answerto = request.POST.dict().get('answerto')
        #is_comment_to_comment = False
        if answerto:
            if isinstance(answerto, str) and answerto.isdigit():
                answerto = int(answerto)
                comment = Comment.objects.filter(id = answerto)
                if comment.exists():
                    comment = comment.first()
                    if comment.author == request.user:
                        form = CommentForm(instance = comment, data = request.POST, files = request.FILES)
                    else:
                        form = CommentForm(data = request.POST, files = request.FILES)
                        form.instance.commented_object = comment
                        #is_comment_to_comment = True
                else:
                    return HttpResponseBadRequest()
            else:
                return HttpResponseBadRequest()
        else:
            form = CommentForm(data = request.POST, files = request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.commented_object:
            form.instance.commented_object = self.object
        form.save()
        return super(QuestionDetailView, self).form_valid(form)
    def form_invalid(self, form):
        return super(QuestionDetailView, self).form_invalid(form)

class NoteDetailView(DetailView):
    model = Note
    template_name = 'note_detail.html'

from django.views.generic.detail import DetailView
from .models import Note

# Create your views here.

class NoteDetailView(DetailView):
    model = Note
    template_name = 'note.html'

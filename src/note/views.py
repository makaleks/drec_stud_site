from django.views.generic.list import ListView
from .models import Note

# Create your views here.

class NoteListView(ListView):
    model = Note
    template_name = 'note_list.html'

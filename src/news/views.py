from django.shortcuts import render
from django.views.generic.list import ListView
from django.shortcuts import redirect
from django.http import HttpResponse
import datetime

from .models import News
from .forms import ArchiveSelectForm

# Create your views here.

class NewsListView(ListView):
    template_name = 'news_list.html'
    model = News
    # get for last month
    def get_queryset(self):
        queryset = News.objects.all()
        years = self.request.GET.get('years')
        if not years:
            now = datetime.datetime.now()
            last = now.replace(year = now.year if now.month > 1 else now.year - 1,
            month = now.month - 1 if now.month > 1 else 12)
            queryset = queryset.filter(edited__gt = last).order_by('-created')
        else:
            queryset = queryset.filter(created__year__in = years.split('-')).order_by('-created')
        return queryset

def archive_draw(request):
    return render(request, 'archive_select.html', {'form': ArchiveSelectForm()})

def archive_process(request):
    # use 'name' from urls.py
    lst = request.GET.getlist('vals')
    s = '/{}'.format('' if not lst else '?years={}'.format('-'.join(lst)))
    return redirect(s)

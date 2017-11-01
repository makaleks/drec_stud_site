from django.shortcuts import render
from django.views.generic.list import ListView
from django.shortcuts import redirect
from django.utils import timezone
import datetime

from .models import News
from .forms import ArchiveSelectForm

# Create your views here.

class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    render_archive = True
    show_hidden = False
    # get for last month
    def get_queryset(self):
        queryset = News.objects.all()
        years = self.request.GET.get('years')
        news = self.request.GET.get('news')
        if not years and not news:
            now = timezone.now()
            days = range(2)
            for i in days:
                try:
                    last = now.replace(year = now.year - 1,
                        month = now.month 
                            if now.day != 1 
                            else now.month - 1 
                                if now.month != 1 
                                else 12, 
                        day = (now - datetime.timedelta(days = 1 + i)).day)
                    break
                except Exception as e:
                    if i == len(days) - 1:
                        raise
            queryset = queryset.filter(edited__gt = last).order_by('-created')
        else:
            if years:
                queryset = queryset.filter(created__year__in = years.split('-')).order_by('-created')
            if news:
                queryset = queryset.filter(pk__in = news.split('-')).order_by('-created')
                # Show like DetailView list
                self.render_archive = False
                self.show_hidden = True
        return queryset
    # Template context
    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context['render_archive'] = self.render_archive
        context['show_hidden'] = self.show_hidden
        return context

def archive_draw(request):
    return render(request, 'archive_select.html', {'form': ArchiveSelectForm()})

def archive_process(request):
    # use 'name' from urls.py
    lst = request.GET.getlist('vals')
    if '-1' in lst: lst.remove('-1')
    s = '/{}'.format('' if not lst else '?years={}'.format('-'.join(lst)))
    return redirect(s)

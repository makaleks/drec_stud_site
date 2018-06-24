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
        # Get last year=today-year
        if not years and not news:
            now = timezone.now()
            days = range(2)
            # For case 29 February
            for i in days:
                try:
                    last = now.replace(year = now.year - 1,
                        month = now.month 
                            if now.day != 1 
                            else now.month - 1 
                                if now.month != 1 
                                else 12, 
                        # 29 February
                        day = (now - datetime.timedelta(days = 1 + i)).day)
                    break
                except Exception as e:
                    if i == len(days) - 1:
                        raise
            queryset = queryset.filter(edited__gt = last).order_by('-created')
        else:
            y_queryset = None
            n_queryset = None
            if years:
                y_queryset = queryset.filter(created__year__in = years.split('-'))
            if news:
                n_queryset = queryset.filter(pk__in = news.split('-'))
                # Show like DetailView list
                if not years:
                    self.show_hidden = True
            self.render_archive = False
            if y_queryset and n_queryset:
                queryset = (y_queryset | n_queryset).order_by('-created')
            elif y_queryset:
                queryset = y_queryset.order_by('-created')
            elif n_queryset:
                queryset = n_queryset.order_by('-created')
            else:
                queryset = News.objects.none()
        return queryset
    # Template context
    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context['render_archive'] = self.render_archive
        context['show_hidden'] = self.show_hidden
        context['last_year'] = timezone.now().date().year - 1
        return context

def archive_draw(request):
    return render(request, 'archive_select.html', {'form': ArchiveSelectForm()})

def archive_get(request):
    # use 'name' from urls.py
    lst = request.GET.getlist('vals')
    if '-1' in lst: 
        lst.remove('-1')
    s = '/{}'.format('' if not lst else '?years={}'.format('-'.join(lst)))
    return redirect(s)

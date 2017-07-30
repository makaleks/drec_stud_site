from django.shortcuts import render
from django.views.generic.list import ListView
from .models import News

# Create your views here.

class NewsListView(ListView):
    template_name = 'news_list.html'
    model = News

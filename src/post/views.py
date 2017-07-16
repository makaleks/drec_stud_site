from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Post

# Create your views here.

class PostList(ListView):
    template_name = "post_list.html"
    model = Post

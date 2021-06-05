from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Comment

# Create your views here.

# Remove last URL part and delete comment
def delete_comment_view(request, *args, **kwargs):
    path = request.path
    splitted = path.rsplit('/')
    if not splitted[-1]:
        splitted = splitted[:-1]
    path = ''
    # Delete the last part of URL
    splitted = splitted[:-1]
    for s in splitted:
        path += s + '/'
    # Finished path creation
    if not request.user.is_authenticated:
        return HttpResponseRedirect(path)

    arg = request.GET.get('id')
    comment = Comment.objects.filter(id=arg)
    if comment.exists():
        comment = Comment.objects.get(id=arg)
        if comment.author == request.user:
            comment.delete()
    return HttpResponseRedirect(path)


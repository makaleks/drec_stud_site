from django.shortcuts import render

# Create your views here.

def render_login_success(request):
    return render(request, 'login_success.html', {
        'request': request.user.get_full_name(),
    })

def render_login_fail(request):
    err = request.GET.get('err')
    return render(request, 'login_fail.html', {
        'err': err,
    })

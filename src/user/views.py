from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.conf import settings
from django.http import Http404

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

class EmergencyLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        if not settings.IS_EMERGENCY_LOGIN_MODE:
            raise Http404()
        else:
            return super(EmergencyLoginView,self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        if not settings.IS_EMERGENCY_LOGIN_MODE:
            raise Http404()
        else:
            return super(EmergencyLoginView,self).post(request, *args, **kwargs)

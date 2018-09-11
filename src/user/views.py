from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from django.views.generic import TemplateView

import urllib

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

class UserUidSetView(TemplateView):
    template_name = 'uid_set.html'
    status = ''
    def get_context_data(self, **kwargs):
        context = super(UserUidSetView, self).get_context_data(**kwargs)
        note = {}
        if self.status:
            status = self.status
            note['enabled'] = True
            note['type'] = status
            if status == 'success':
                note['text'] = 'Карта успешно привязана к аккаунту.'
            elif status == 'info':
                note['text'] = 'Вы ничего не ввели'
        context['notification'] = note
        return context
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        status = data.get('status')
        if status:
            self.status = status
        return super(UserUidSetView, self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        status = ''
        if request.user.is_authenticated:
            user = request.user
            data = request.POST.dict()
            if data.get('uid'):
                user.card_uid = data['uid']
                user.save()
                status = 'success'
                return HttpResponseRedirect('/user/long-logout?next=/user/uid%3Fvk_exiter%3Dstop&n12n-enable=1&n12n-type=success&timeout=5&n12n-text={0}'.format(urllib.parse.quote('Карта успешно привязана к аккаунту.')))
            else:
                status = 'info'
        return HttpResponseRedirect('?status={0}'.format(status))

def long_logout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    timeout = request.GET.get('timeout')
    if not timeout:
        timeout = 3
    next_page = request.GET.get('next')
    logout_text = request.GET.get('logout_text')
    return render(request, 'long_logout.html', {
        'timeout': timeout,
        'next': next_page,
        'logout_text': logout_text
    })


from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from django.views.generic import TemplateView

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
            else:
                status = 'info'
        return HttpResponseRedirect('?status={0}'.format(status))



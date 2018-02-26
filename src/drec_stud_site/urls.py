"""drec_stud_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, handler400, handler403, handler404, handler500
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
#from user.views import render_login_success
from user.views import EmergencyLoginView

handler400 = 'utils.views.error_view_400'
handler403 = 'utils.views.error_view_403'
handler404 = 'utils.views.error_view_404'
handler500 = 'utils.views.error_view_500'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^social/', include('social_django.urls', namespace='social')),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^login/$', EmergencyLoginView.as_view(template_name='core/login.html'), name='emergency-login'),
    url(r'^services/', include('service.urls')),
    url(r'^surveys/', include('survey.urls')),
    url(r'^notes/', include('note.urls')),
    url(r'^', include('news.urls')),
    #url(r'^login_success/', render_login_success),
    #url(r'^login/', TemplateView.as_view(template_name='login.html')),
]

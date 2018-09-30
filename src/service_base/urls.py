from django.urls import path, include 
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .views import ServiceListView

def collect_urls():
    result = []
    for s in settings.SERVICE_CHILDREN:
        result.append(
            path(s + '/', include(s + '.urls'))
        )
    return result

urlpatterns = [
    path('', csrf_exempt(ServiceListView.as_view())),
] + collect_urls()

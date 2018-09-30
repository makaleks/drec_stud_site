from django.urls import path, include 
from django.conf import settings

from service_base.proxy_views import view_proxy_factory

from .views import WashingDetailView
from .models import Washing

# Must be set to use namespaces
app_name = 'washing'

urlpatterns = [
    path('<int:order>/', view_proxy_factory(Washing, 
                WashingDetailView.as_view()), name = 'washing_detail'),
    path('', view_proxy_factory(Washing, 
                WashingDetailView.as_view()), name = 'washing_base'),
]

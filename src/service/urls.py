from django.urls import path
from .views import unlock, list_update, ServiceListView, ServiceDetailView
from django.views.decorators.csrf import csrf_exempt

app_name = 'service'
urlpatterns = [
    path('<slug:slug>/list-update/', list_update, name = 'list-update'),
    path('<slug:slug>/unlock/',      unlock, name = 'unlock'),
    path('<slug:slug>/',             ServiceDetailView.as_view(), name = 'service'),
    # Needed to get money
    path('',                         csrf_exempt(ServiceListView.as_view()), name = 'service-list'),
]

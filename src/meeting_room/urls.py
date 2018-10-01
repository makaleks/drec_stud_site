from django.urls import path, include 
from django.conf import settings

from service_base.proxy_views import view_proxy_factory

from service_item.lock_api import gen_api_path
from .views import MeetingRoomDetailView
from .models import MeetingRoom, Order

# Must be set to use namespaces
app_name = 'meeting_room'

urlpatterns = [
    path('<int:order>/', view_proxy_factory(MeetingRoom, 
                MeetingRoomDetailView.as_view()), name = 'room_detail'),
    path('', view_proxy_factory(MeetingRoom, 
                MeetingRoomDetailView.as_view()), name = 'room_base'),
] + gen_api_path(MeetingRoom, Order)

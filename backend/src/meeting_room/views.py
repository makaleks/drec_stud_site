from django.shortcuts import render
from django.http import HttpResponseRedirect

from service_document.views import OrderApprovingAbstractView
from .models import MeetingRoom, Order

# Create your views here.

class MeetingRoomDetailView(OrderApprovingAbstractView):
    model = MeetingRoom
    template_name = 'meeting_room_timetable.html'
    context_object_name = 'service'
    def post(self, request, *args, **kwargs):
        # From OrderApprovingAbstractView
        approved = self.approve(request, Order, *args, **kwargs)
        # From ItemOrderingAbstractView
        status = self.order(request, Order, *args, **kwargs)
        if status:
            if status['type'] == 'success':
                status['type'] = 'primary'
                status['text'] = 'Заявка зарегистрирована. Осталось принести служебку. При наличии нескольких претендентов, удовлетворена будет заявка первого предъявившего служебку.'
            elif status['type'] == 'info' and approved:
                status['type'] = 'success'
                status['text'] = 'Успех'
        return HttpResponseRedirect(self.status_to_url(status))


from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
import datetime
import json
import re
from .models import Order

# Create your views here.

def unlock(request, service_name):
    uid = request.GET.get('uid')
    today = datetime.datetime.now()
    orders = Order.objects.all().filter(Q(user__uid = uid, item__service__url_id = service_name, date_start = today.date(), time_start__lte = today.time()) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))))
    #return HttpResponse(str([vars(o) for o in orders]))
    if orders:
        return HttpResponse('yes')
    else:
        return HttpResponse('no')

def to_H_M(t):
    return re.sub(r'(?P<part>^|:)0', '\g<part>', t.strftime('%H:%M'))

def list_update(request, service_name):
    today = datetime.datetime.now()
    orders = Order.objects.all().filter(Q(date_start = today.date()) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))) | Q(date_start__gt = today.date())).order_by('date_start', 'time_end')
    return HttpResponse(json.dumps([{'uid': o.user.uid, 'date_start': str(o.date_start), 'time_start': to_H_M(o.time_start), 'time_end': to_H_M(o.time_end)} for o in orders]))

from django.http import HttpResponse
from django.urls import path 

import json
import datetime
import re

from service_base.utils import order_to_pk
from user.models import User
from .utils import to_dt

import logging
lock_logger = logging.getLogger('lock_api_logs')

def log_and_response(scenario, card_uid, service_model, service_order):
    s = 'Scenario:\n{0}\n####################'.format(json.dumps(scenario, indent = 2, ensure_ascii = False))
    if scenario['status'] == 'no':
        s = 'Got service  = {0}({1})\nGot card_uid = {2}\n'.format(service_model, service_order, card_uid) + s
        lock_logger.error(s)
    else:
        lock_logger.info(s)
    return HttpResponse(json.dumps(scenario))


# Check unlock
# test with:
# bash$ curl 'http://localhost/services/washing/unlock/?uid=200'
def unlock(request, service_model, order_model, service_order = 1):
    # The order of checks is important!
    lock_logger.critical('hello from lock_api')
    card_uid, vk_id = request.GET.get('uid'), None
    if card_uid is None:
        vk_id = request.GET.get('vk_id')
    scenario = {
        'success': {
            'status': 'yes',
            'cause' : 'success',
            # Remember to set the name!
            'name'  : '',
        },
        'no_orders': {
            'status': 'no',
            'cause' : 'no_orders',
            # Remember to set the name!
            'name'  : '',
        },
        'staff': {
            'status': 'yes',
            'cause' : 'staff',
            # Remember to set the name!
            'name'  : '',
        },
        'unknown_service': {
            'status': 'no',
            'cause' : 'unknown_service',
            'name'  : '',
        },
        'unknown_user': {
            'status': 'no',
            'cause' : 'unknown_user',
            'name'  : '',
        },
        'lock_disabled': {
            'status': 'yes',
            'cause' : 'lock_disabled',
            'name'  : '',
        },
    }
    # At least one of `card_uid` or `vk_id` should be in request params
    if not card_uid and not vk_id:
        return HttpResponse(json.dumps(scenario['unknown_user']))
    # disable unknown services
    pk = order_to_pk(service_model, service_order)
    if pk is None:
        response = scenario['unknown_service']
        return log_and_response(response, card_uid, service_model, service_order)
    service = service_model.objects.get(pk = pk)
    # emergency mode
    if service.disable_lock:
        response = scenario['lock_disabled']
        return log_and_response(response, card_uid, service_model, service_order)
    # disable unknown users
    pred = (
        User.objects.all().filter(card_uid=card_uid)
        if card_uid is not None else
        User.objects.all().filter(account_id=vk_id)
    )
    if not pred.exists():
        response = scenario['unknown_user']
        return log_and_response(response, card_uid, service_model, service_order)
    # pass all staff
    user = pred.first()
    if (card_uid or vk_id) and user.is_staff:
        response = scenario['staff']
        response['name'] = user.get_full_name()
        return log_and_response(response, card_uid, service_model, service_order)
    # process orders check
    now = datetime.datetime.now()
    time_margin_start = datetime.datetime.combine(datetime.date.min, service.time_margin_start) - datetime.datetime.min
    time_margin_end = datetime.datetime.combine(datetime.date.min, service.time_margin_end) - datetime.datetime.min

    # Interval = 1sec. as an alternative to 1 moment
    interval = datetime.timedelta(seconds = 0.5)
    tmp = order_model.get_queryset(now - interval, now + interval, time_margin_start, time_margin_end)
    if card_uid:
        orders = tmp.filter(item__service=service, user__card_uid=card_uid)
    else:
        orders = tmp.filter(item__service=service, user__account_id=vk_id)
    if orders:
        # Check endings - 'is_used' required
        order_lst = list(orders)
        unlock = False
        for o in order_lst:
            [start, end] = to_dt(o.date_start, o.time_start, o.time_end).values()
            if end >= now:
                unlock = True
                o.is_used = True
                o.save()
            elif o.is_used:
                unlock = True
        if unlock:
            response = scenario['success']
            response['name'] = user.get_full_name()
            return log_and_response(response, card_uid, service_model, service_order)
    response = scenario['no_orders']
    response['name'] = user.get_full_name()
    return log_and_response(response, card_uid, service_model, service_order)

def to_H_M(t):
    #???
    #return re.sub(r'(?P<part>^|:)0', '\g<part>', t.strftime('%H:%M'))
    return t.strftime('%H:%M')

# Get many orders to work offline
def list_update(request, service_model, order_model, service_order = 1):
    dt_from = datetime.datetime.now()
    dt_to = dt_from + datetime.timedelta(days = 2)
    pk = order_to_pk(service_model, service_order)
    if pk is None:
        return HttpResponse('Error: unknown {0}-{1}'.format(str(service_model), str(service_order)))
    service = service_model.objects.get(pk = pk)
    orders = order_model.get_queryset(dt_from, dt_to).filter(item__service = service)

    return HttpResponse(json.dumps([{'uid': o.user.card_uid, 'name': o.user.get_full_name(), 'date_start': str(o.date_start), 'time_start': to_H_M(o.time_start), 'time_end': to_H_M(o.time_end)} for o in orders]))

# Returns path() for unlock() and list_update()
def gen_api_path(service_model, order_model):
    return [
        path('<int:service_order>/unlock/', unlock, {'service_model': service_model, 'order_model': order_model}),
        path('unlock/', unlock, {'service_model': service_model, 'order_model': order_model}),
        path('<int:service_order>/list-update/', list_update, {'service_model': service_model, 'order_model': order_model}),
        path('list-update/', list_update, {'service_model': service_model, 'order_model': order_model}),
        ]


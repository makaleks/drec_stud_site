from .models import ServiceBase
from .utils import to_dt
from service_base.utils import order_to_pk

# TODO FIX ALL

# Check unlock
# test with:
# bash$ curl 'http://localhost/services/washing/unlock/?uid=200'
def unlock(request, service_model, service_order = 1, order_model):
    # The order of checks is important!
    card_uid = request.GET.get('uid')
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
    # disable unknown services
    pk = order_to_pk(service_model, service_order)
    if pk is None:
        response = scenario['unknown_service']
        return HttpResponse(json.dumps(response))
    service = service_model.objects.get(pk)
    # emergency mode
    if service.disable_lock:
        response = scenario['lock_disabled']
        return HttpResponse(json.dumps(response))
    # disable unknown users
    if not User.objects.all().filter(card_uid = card_uid).exists():
        response = scenario['unknown_user']
        return HttpResponse(json.dumps(response))
    # pass all staff
    user = User.objects.all().filter(card_uid = card_uid).first()
    if card_uid and user.is_staff:
        response = scenario['staff']
        response['name'] = user.get_full_name()
        return HttpResponse(json.dumps(response))
    # process orders check
    now = datetime.datetime.now()
    time_margin_start = datetime.datetime.combine(datetime.date.min, service.time_margin_start) - datetime.datetime.min
    time_margin_end = datetime.datetime.combine(datetime.date.min, service.time_margin_end) - datetime.datetime.min

    # Interval = 1sec. as an alternative to 1 moment
    interval = datetime.timedelta(seconds = 0.5)
    orders = order_model.get_queryset(now - interval, now + interval, time_margin_start, time_margin_end).filter(user__card_uid = card_uid)
    if orders:
        # Check endings - 'used' required
        order_lst = list(orders)
        unlock = False
        for o in order_lst:
            [start, end] = to_dt(o.date_start, o.time_start, o.time_end)
            if end >= now:
                unlock = True
                o.used = True
                o.save()
            elif o.used:
                unlock = True
        if unlock:
            response = scenario['success']
            response['name'] = user.get_full_name()
            return HttpResponse(json.dumps(response))
    response = scenario['no_orders']
    response['name'] = user.get_full_name()
    return HttpResponse(json.dumps(response))

def to_H_M(t):
    return re.sub(r'(?P<part>^|:)0', '\g<part>', t.strftime('%H:%M'))

# get orders
def list_update(request, slug):
    today = timezone.now()
    orders = Order.objects.all().filter(Q(date_start = today.date(), item__service__slug = slug) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))) | Q(date_start__gt = today.date())).order_by('date_start', 'time_end')
    return HttpResponse(json.dumps([{'uid': o.user.card_uid, 'name': o.user.get_full_name(), 'date_start': str(o.date_start), 'time_start': to_H_M(o.time_start), 'time_end': to_H_M(o.time_end)} for o in orders]))


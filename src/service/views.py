from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import datetime
import json
import re
import hashlib
from user.models import User
from .models import Order, Item, Service, Participation

import logging
payment_logger = logging.getLogger('payment_logs')

# Create your views here.

# Check unlock
def unlock(request, slug):
    card_uid = request.GET.get('uid')
    today = timezone.now()
    orders = Order.objects.all().filter(Q(user__card_uid = card_uid, item__service__slug = slug, date_start = today.date(), time_start__lte = today.time()) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))))
    #return HttpResponse(str([vars(o) for o in orders]))
    if orders:
        return HttpResponse('yes')
    else:
        return HttpResponse('no')

def to_H_M(t):
    return re.sub(r'(?P<part>^|:)0', '\g<part>', t.strftime('%H:%M'))

# get orders
def list_update(request, slug):
    today = timezone.now()
    orders = Order.objects.all().filter(Q(date_start = today.date(), item__service__slug = slug) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))) | Q(date_start__gt = today.date())).order_by('date_start', 'time_end')
    return HttpResponse(json.dumps([{'uid': o.user.card_uid, 'date_start': str(o.date_start), 'time_start': to_H_M(o.time_start), 'time_end': to_H_M(o.time_end)} for o in orders]))

def _is_decimal(s):
    try:
        Decimal(s)
        return True
    except ValueError:
        return False
def _is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class ServiceListView(ListView):
    model = Service
    template_name = 'service_list.html'
    # yandex payment logic
    def post(self, request, *args, **kwargs):
        log_error = False
        log_str = '\n'
        try:
            def _create_lost_str(data):
                to_ret = ''
                required_keys = ['notification_type', 'operation_id', 'amount', 'currency', 'datetime', 'sender', 'codepro', 'label', 'sha1_hash']
                for field in required_keys:
                    if not field in data:
                        to_ret += '\'{0}\'\n'.format(field)
                return to_ret
            data = request.POST.dict()
            user_id = data.get('label', '')
            # 'payed' != 'recieved', set by 'payed'
            amount = data.get('withdraw_amount', '')
            lost_str = _create_lost_str(data)
            if lost_str:
                log_error = True
                log_str += '- FIELD_ERROR - the following fields were not found:\n{0}'.format(lost_str)
            elif user_id and _is_int(user_id) and int(user_id) > 0 and _is_decimal(amount) and Decimal(amount) > 0:
                user = User.objects.filter(id = user_id)
                if not user.exists():
                    log_error = True
                    log_str += '- NO_USER - can`t add {0}$ to account with id={1}\n'.format(amount, user_id)
                else:
                    user = user.first()
                    # BE CAREFUL with the following code!
                    # See https://tech.yandex.com/money/doc/dg/reference/notification-p2p-incoming-docpage/#verify-notification
                    hash_source = '{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{notification_secret}&{label}'.format(
                            notification_type = data['notification_type'],
                            operation_id = data['operation_id'],
                            amount = data['amount'],
                            currency = data['currency'],
                            datetime = data['datetime'],
                            sender = data['sender'],
                            codepro = data['codepro'],
                            notification_secret = settings.PAYMENT_SECRET_YANDEX,
                            label = data['label']
                    ).encode('utf-8')
                    m = hashlib.sha1(hash_source)
                    if m.hexdigest() != data['sha1_hash']:
                        log_error = True
                        log_str += '- HASH_ERROR - required {0} != recieved {1}\n'.format(m.hexdigest(), data['sha1_hash'])
                    else:
                        user.account += Decimal(amount)
                        user.save()
                        log_str += '- SUCCESS - for user {0}({1}) +{2} = {3}\n'.format(user_id, user.get_full_name(), amount, user.account)
            else:
                log_error = True
                log_str += '- FORMAT_ERROR - some error with user_id(\'label\')={0} and amount(\'withdraw_amount\')={1}\n'.format(user_id, amount)
        except Exception as e:
            log_str += str(e)
        log_str += '####################'
        if log_error:
            log_str = '\n- Got {0}'.format(str(data)) + log_str
            payment_logger.error(log_str)
        else:
            payment_logger.info(log_str)
        # Return OK to yandex
        return HttpResponse(status=200)

class ServiceDetailView(DetailView):
    model = Service
    status = ''
    def get_template_names(self):
        return ['service_timetable.html' if not self.object.is_single_item else 'service_timetable_single.html']
    def get_context_data(self, **kwargs):
        context = super(ServiceDetailView, self).get_context_data(**kwargs)
        note = {}
        if self.status:
            status = self.status
            note['enabled'] = True
            note['type'] = self.status
            if status == 'success':
                note['text'] = 'Успех!'
            elif status == 'info':
                note['text'] = 'Заявка зарегистрирована. Осталось принести служебку. При наличии нескольких претендентов, удовлетворена будет заявка первого предъявившего служебку.'
            elif status == 'warning':
                note['text'] = 'Недостаточно средств на счёте'
            else:
                note['text'] = 'Это уведомление не должно было появиться! Сообщите о нём администрации'
                note['type'] = 'danger'
        context['notification'] = note
        if self.object.request_document:
            to_approve = list(self.object.items.first().orders.all().filter(is_approved = False))
            context['to_approve'] = to_approve
        return context
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        status = data.get('status')
        if status:
            self.status = status
        return super(ServiceDetailView, self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        status = ''
        if request.user.is_authenticated:
            # TODO: check required 'Rules accepted' checkbox
            self.object = self.get_object()
            status = 'success'
            is_approved = True
            data = request.POST.dict()
            now = timezone.now()
            service_td = datetime.datetime.combine(datetime.date.min, self.object.time_after_now) - datetime.datetime.min
            # Change the 2 following lines to enable #cancel_late_order
            #before_now_time = now - service_td
            #after_now_time = now + service_td
            before_now_time = now 
            after_now_time = now
            if data.get('type') == 'order':
                order_lst = []
                undo_order_ids = []
                undo_order_lst = []
                participation_lst = []
                title = data['title'] if data.get('title') else ''
                if self.object.request_document:
                    is_approved = False
                    status = 'info'
                for k in data.keys():
                    if k[:6] == 'order=':
                        tmp = k[6:].split('&&')
                        order_lst.append({'name': tmp[0], 'time_start': datetime.datetime.strptime(tmp[1], '%H:%M').time(), 'time_end': datetime.datetime.strptime(tmp[2], '%H:%M').time(), 'date_start': datetime.datetime.strptime(tmp[3], '%Y-%m-%d').date()})
                    if k[:14] == 'participation=':
                        participation_lst.append(k[14:])
                    if k[:7] == 'cancel=':
                        undo_order_ids.append(int(k[7:]))
                undo_order_lst = list(
                        Order.objects.filter(
                            Q(date_start__gt=before_now_time.date()) 
                            | (
                                Q(date_start__exact=before_now_time.date()) 
                                & Q(time_start__gte=before_now_time.time())
                                ), user = request.user,
                            id__in=undo_order_ids))
                items = list(Item.objects.all())
                items_dict = {}
                for i in items:
                    items_dict[i.name] = i
                total_price = 0
                for l in order_lst:
                    total_price += items_dict[l['name']].get_price()
                for l in undo_order_lst:
                    if after_now_time * 2 > datetime.datetime.combine(l.date_start, l.time_start):
                        total_price -= int(l.payed * self.object.late_cancel_multiplicator)
                    else:
                        total_price -= l.payed
                exception_participations = [l[0] for l in list(Participation.objects.all().filter(id__in = participation_lst).values_list('id'))]
                participation_lst = list(filter(lambda el: el not in exception_participations, participation_lst))
                # We will save participations if order (even zero-length)
                # also can be saved, so if it is possible to save 
                # part. but not to save orders nothing will be saved

                #data['success'] = False
                final_orders = []
                if request.user.account >= total_price:
                    # Can`t use bulk_create because 
                    # it does not call save() and pre_save and post_save
                    for l in order_lst:
                        final_orders.append(Order(date_start = l['date_start'], 
                            time_start = l['time_start'], time_end = l['time_end'],
                            item = items_dict[l['name']], user = request.user, title = title, is_approved = is_approved, payed = items_dict[l['name']].get_price()))
                    for o in final_orders:
                        o.clean()
                    for o in final_orders:
                        o.save()
                    for o in undo_order_lst:
                        o.delete()
                    request.user.account -= total_price
                    request.user.save()

                    for p in participation_lst:
                        Participation(order_id = p, user = request.user).save()
                    if participation_lst and not final_orders:
                        status = 'success'
                else:
                    status = 'warning'

                #tmp = data['name'].split('&&')
                #data['result'] = str(total_price)
                #return HttpResponse(final_orders)
            elif data.get('type') == 'approve' and request.user.is_staff:
                lst = []
                for k in data.keys():
                    if k[:3] == 'id=':
                        lst.append(k[3:])
                orders = Order.objects.all().filter(pk__in=lst)
                for o in orders:
                    o.is_approved = True
                    o.save()
            else:
                status = 'danger'
        return HttpResponseRedirect('?status={0}'.format(status))

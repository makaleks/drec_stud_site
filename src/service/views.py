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
from user.models import User
from .models import Order, Item, Service, Participation

# TODO: REMOVE THIS!!!
import os

# Create your views here.

def unlock(request, slug):
    uid = request.GET.get('uid')
    today = timezone.now()
    orders = Order.objects.all().filter(Q(user__uid = uid, item__service__slug = slug, date_start = today.date(), time_start__lte = today.time()) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))))
    #return HttpResponse(str([vars(o) for o in orders]))
    if orders:
        return HttpResponse('yes')
    else:
        return HttpResponse('no')

def to_H_M(t):
    return re.sub(r'(?P<part>^|:)0', '\g<part>', t.strftime('%H:%M'))

def list_update(request, slug):
    today = timezone.now()
    orders = Order.objects.all().filter(Q(date_start = today.date(), item__service__slug = slug) & (Q(time_end__gt = today.time()) | Q(time_end = datetime.time(0,0,0))) | Q(date_start__gt = today.date())).order_by('date_start', 'time_end')
    return HttpResponse(json.dumps([{'uid': o.user.uid, 'date_start': str(o.date_start), 'time_start': to_H_M(o.time_start), 'time_end': to_H_M(o.time_end)} for o in orders]))

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
    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        user_id = data['label']
        amount = data['withdraw_amount']
        if user_id and _is_int(user_id) and int(user_id) > 0 and _is_decimal(amount):
            user = User.objects.get(id = user_id)
            if not user or not user.is_authenticated:
                f = open(os.path.join(settings.MEDIA_ROOT, 'error_pay {0}.txt'.format(datetime.datetime.now())), 'w')
                f.write(str(data))
                f.close()
            else:
                user.account += Decimal(amount)
                user.save()
        # TODO: REMOVE THIS!
        f = open(os.path.join(settings.MEDIA_ROOT, 'root post {0}.txt'.format(datetime.datetime.now())), 'w')
        f.write(str(data))
        f.close()
        return HttpResponse(str(data))

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
        if self.object.is_single_item:
            to_approve = list(self.object.items.first().orders.all().filter(approved = False))
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
            approved = True
            data = request.POST.dict()
            if data.get('type') == 'order':
                order_lst = []
                participation_lst = []
                title = data['title'] if data.get('title') else ''
                if self.object.request_document:
                    approved = False
                    status = 'info'
                for k in data.keys():
                    if k[:6] == 'order=':
                        tmp = k[6:].split('&&')
                        order_lst.append({'name': tmp[0], 'time_start': datetime.datetime.strptime(tmp[1], '%H:%M').time(), 'time_end': datetime.datetime.strptime(tmp[2], '%H:%M').time(), 'date_start': datetime.datetime.strptime(tmp[3], '%Y-%m-%d').date()})
                    if k[:14] == 'participation=':
                        participation_lst.append(k[14:])
                names = []
                for l in order_lst:
                    names.append(l['name'])
                items = list(Item.objects.all())
                items_dict = {}
                for i in items:
                    items_dict[i.name] = i
                total_price = 0
                for l in order_lst:
                    total_price += items_dict[l['name']].get_price()
                exception_participations = [l[0] for l in list(Participation.objects.all().filter(id__in = participation_lst).values_list('id'))]
                participation_lst = filter(lambda el: el not in exception_participations, participation_lst)
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
                            item = items_dict[l['name']], user = request.user, title = title, approved = approved))
                    for o in final_orders:
                        o.clean()
                    for o in final_orders:
                        o.save()
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
            elif data.get('type') == 'approve':
                lst = []
                for k in data.keys():
                    if k[:3] == 'id=':
                        lst.append(k[3:])
                orders = Order.objects.all().filter(pk__in=lst)
                for o in orders:
                    o.approved = True
                    o.save()
        return HttpResponseRedirect('?status={0}'.format(status))

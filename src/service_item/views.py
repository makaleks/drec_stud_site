from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.db.models import Q

import datetime
import urllib

# Create your views here.

# The abstract class to order items for money
# The model must be inherited from ServiceAbstract (see models.py)
class ItemOrderingAbstractView(DetailView):
    def get_context_data(self, **kwargs):
        context = super(ItemOrderingAbstractView, self).get_context_data(**kwargs)
        context['time_list'] = self.object.gen_timetable_layout(self.request.user)
        return context
    # Returns status string as URL parameters
    @staticmethod
    def status_to_url(status_dict):
        if not status_dict:
            return ''
        else:
            return '?n12n-enable=1&n12n-type={0}&n12n-text={1}'.format(
                        status_dict['type'],
                        status_dict['text']
                    )
    # Returns {} or {'type', 'text'}, use status_to_url for HttpResponse
    def order(self, request, order_model, *args, **kwargs):
        status_to_ret = {}
        if request.user.is_authenticated:
            status_success = {
                    'type': 'success',
                    'text': 'Успех!',
                }
            status_no_money = {
                    'type': 'warning',
                    'text': 'Недостаточно средств на счёте',
                }
            status_idle = {
                    'type': 'info',
                    'text': 'Вы ничего не выбрали',
                }

            status_to_ret = status_success
            # TODO: check required 'Rules accepted' checkbox
            obj = self.get_object()
            now = datetime.datetime.now()
            data = request.POST.dict()
            service_td = datetime.datetime.combine(datetime.date.min, obj.time_after_now) - datetime.datetime.min
            # Change the 2 following lines to enable #cancel_late_order
            undo_start = now - service_td
            #undo_start = now

            order_lst = []
            undo_order_ids = []
            undo_order_lst = []
            for k in data.keys():
                if k[:6] == 'order=':
                    tmp = k[6:].split('&&')
                    order_lst.append({'name': tmp[0], 'time_start': datetime.datetime.strptime(tmp[1], '%H:%M').time(), 'time_end': datetime.datetime.strptime(tmp[2], '%H:%M').time(), 'date_start': datetime.datetime.strptime(tmp[3], '%Y-%m-%d').date()})
                if k[:7] == 'cancel=':
                    undo_order_ids.append(int(k[7:]))
            # If all is empty
            if not order_lst and not undo_order_ids:
                status_to_ret = status_idle
                return status_to_ret
            undo_order_lst = list(
                    order_model.objects.filter(
                                id__in = undo_order_ids,
                                user = request.user
                            ).filter(
                                Q(date_start__gt = undo_start.date())
                                | Q(date_start = undo_start.date(),
                                    time_start__gte = undo_start.time()
                                )
                            )
                )
            items = list(obj.items.all())
            items_dict = {}
            for i in items:
                items_dict[i.name] = i
            total_price = 0
            for l in order_lst:
                total_price += items_dict[l['name']].get_price()
            for l in undo_order_lst:
                if now > datetime.datetime.combine(l.date_start, l.time_start):
                    total_price -= int(l.payed * obj.late_cancel_multiplicator)
                else:
                    total_price -= l.payed

            final_orders = []
            if request.user.account >= total_price:
                # Can`t use bulk_create because 
                # it does not call save(), pre_save and post_save
                for l in order_lst:
                    kwargs = {
                            'date_start': l['date_start'], 
                            'time_start': l['time_start'], 
                            'time_end': l['time_end'], 
                            'item': items_dict[l['name']], 
                            'user': request.user,
                        }
                    if hasattr(order_model, 'payed'):
                        kwargs['payed'] = items_dict[l['name']].get_price()
                    final_orders.append(order_model(**kwargs))
                for o in final_orders:
                    o.clean()
                for o in final_orders:
                    o.save()
                for o in undo_order_lst:
                    o.delete()
                request.user.account -= total_price
                request.user.save()

            else:
                status_to_ret = status_no_money

            #tmp = data['name'].split('&&')
            #data['result'] = str(total_price)
            #return HttpResponse(final_orders)
        return status_to_ret


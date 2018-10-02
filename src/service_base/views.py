from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.conf import settings
from django.apps import apps

from decimal import Decimal
import hashlib


from user.models import User
from .models import ServiceBase

import logging
payment_logger = logging.getLogger('payment_logs')

# Create your views here.

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


class ServiceListView(TemplateView):
    model = ServiceBase
    template_name = 'service_list.html'
    def get_context_data(self, **kwargs):
        context = super(ServiceListView, self).get_context_data(**kwargs)
        service_lst = []
        for app_name in settings.SERVICE_CHILDREN:
            app = apps.get_app_config(app_name)
            for model in app.get_models():
                if issubclass(model, ServiceBase):
                    service_lst.extend(list(model.objects.all()))
        context['service_base_list'] = service_lst
        return context
    # Yandex payment logic - BE ACCURATE
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


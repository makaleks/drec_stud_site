from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.apps import apps

from decimal import Decimal
import hashlib

import hmac
from urllib.parse import urlencode



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

# this code was adopted from inline code inside 'try' - not tested,
# saved for... I don't know what; I'm just afraid to loose it,
# the origin worked seamlessly for 9 years!
def try_apply_input_money_v1(data_dict, error_ctx):
    def _create_lost_str(data_dict):
        to_ret = ''
        required_keys = ['notification_type', 'operation_id', 'amount', 'currency', 'datetime', 'sender', 'codepro', 'label', 'sha1_hash']
        for field in required_keys:
            if not field in data_dict:
                to_ret += '\'{0}\'\n'.format(field)
        return to_ret
    user_id = data_dict.get('label', '')
    # 'payed' != 'recieved', set by 'payed'
    amount = data_dict.get('withdraw_amount', '')
    lost_str = _create_lost_str(data_dict)
    if lost_str:
        error_ctx['log_error'] = True
        error_ctx['log_str'] += '- FIELD_ERROR(v1) - the following fields were not found:\n{0}'.format(lost_str)
    elif user_id and _is_int(user_id) and int(user_id) > 0 and _is_decimal(amount) and Decimal(amount) > 0:
        user = User.objects.filter(id = user_id)
        if not user.exists():
            error_ctx['log_error'] = True
            error_ctx['log_str'] += '- NO_USER(v1) - can`t add {0}$ to account with id={1}\n'.format(amount, user_id)
        else:
            user = user.first()
            # BE CAREFUL with the following code!
            # See https://tech.yandex.com/money/doc/dg/reference/notification-p2p-incoming-docpage/#verify-notification
            hash_source = '{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{notification_secret}&{label}'.format(
                    notification_type = data_dict['notification_type'],
                    operation_id = data_dict['operation_id'],
                    amount = data_dict['amount'],
                    currency = data_dict['currency'],
                    datetime = data_dict['datetime'],
                    sender = data_dict['sender'],
                    codepro = data_dict['codepro'],
                    notification_secret = settings.PAYMENT_SECRET_YANDEX,
                    label = data_dict['label']
            ).encode('utf-8')
            m = hashlib.sha1(hash_source)
            if m.hexdigest() != data_dict['sha1_hash']:
                error_ctx['log_error'] = True
                error_ctx['log_str'] += '- HASH_ERROR(v1) - required {0} != recieved {1}\n'.format(m.hexdigest(), data_dict['sha1_hash'])
            else:
                user.account += Decimal(amount)
                user.save()
                error_ctx['log_str'] += '- SUCCESS(v1) - for user {0}({1}) +{2} = {3}\n'.format(user_id, user.get_full_name(), amount, user.account)
    else:
        error_ctx['log_error'] = True
        error_ctx['log_str'] += '- FORMAT_ERROR(v1) - some error with user_id(\'label\')={0} and amount(\'withdraw_amount\')={1}\n'.format(user_id, amount)

# The new version after yoomoney dropped sha1_hash field in 2026.04.17 without
# any notification. The yoonomey docs were not updated for 5 days so nobody knew
# how to handle the new 'sign' field. In fact the algorithm became absolutly
# different, so I had no chance to guess it
def try_apply_input_money_v2(data_dict, error_ctx):
    params = data_dict.copy()
    received_sign = params.pop('sign', None)

    sorted_params = sorted(params.items())

    query_string = urlencode(sorted_params)

    calculated_sign = hmac.new(
        settings.PAYMENT_SECRET_YANDEX.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # all data collected, now try to save (copy-paste from v1)
    user_id = data_dict.get('label', '')
    # 'payed' != 'recieved', set by 'payed'
    amount = data_dict.get('withdraw_amount', '')
    if user_id and _is_int(user_id) and int(user_id) > 0 and _is_decimal(amount) and Decimal(amount) > 0:
        user = User.objects.filter(id = user_id)
        if not user.exists():
            error_ctx['log_error'] = True
            error_ctx['log_str'] += '- NO_USER(v2) - can`t add {0}$ to account with id={1}\n'.format(amount, user_id)
        else:
            user = user.first()
            if calculated_sign != received_sign:
                error_ctx['log_error'] = True
                error_ctx['log_str'] += '- HASH_ERROR(v2) - required {0} != recieved {1}\n'.format(received_sign, calculated_sign)
            else:
                user.account += Decimal(amount)
                user.save()
                error_ctx['log_str'] += '- SUCCESS(v2) - for user {0}({1}) +{2} = {3}\n'.format(user_id, user.get_full_name(), amount, user.account)
    else:
        error_ctx['log_error'] = True
        error_ctx['log_str'] += '- FORMAT_ERROR(v2) - some error with user_id(\'label\')={0} and amount(\'withdraw_amount\')={1}\n'.format(user_id, amount)


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
        data = request.POST.dict()
        error_ctx = {'log_error': False, 'log_str': '\n'}
        try:
            try_apply_input_money_v2(data, error_ctx)
        except Exception as e:
            error_ctx['log_error'] = True
            error_ctx['log_str'] += str(e) + '\n'
        error_ctx['log_str'] += '####################'
        if error_ctx['log_error']:
            error_ctx['log_str'] = '\n- Got {0}'.format(str(data)) + error_ctx['log_str']
            payment_logger.error(error_ctx['log_str'])
            return HttpResponse(status=500)
        else:
            payment_logger.info(error_ctx['log_str'])
        # Return OK to yandex
        return HttpResponse(status=200)


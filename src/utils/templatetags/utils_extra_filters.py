from django import template
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from user.models import User
from django.forms import ModelForm
import datetime
import re
import json

from service.models import Participation
from comment.models import Comment


register = template.Library()

@register.filter
def util_by_key(dictionary, key):
    return dictionary.get(key)

@register.filter
def util_range(i):
    return range(i)

@register.filter
def util_add_user_info(lst, user):
    if not user.is_anonymous:
        for day in lst:
            for machine in day['items'].values():
                i = 0
                column = machine['time']
                length = len(column)
                while i < length:
                    u = column[i].get('user')
                    if u and u == user:
                        if (i != 0 and 'user' in column[i - 1]
                            and column[i - 1]['user'] != user):
                            column[i - 1].update({'show_info': True})
                        if (i != length - 1 and 'user' in column[i + 1]
                            and column[i + 1]['user'] != user):
                            column[i + 1].update({'show_info': True})
                    id = column[i].get('id')
                    if id and Participation.objects.filter(order = id, user = user):
                        column[i]['participated'] = True
                    i+=1
                machine['time'] = column
    return lst

@register.filter
def util_is_finished(dt_start, service):
    service_td = datetime.datetime.combine(datetime.date.min, service.time_after_now) - datetime.datetime.min
    now = timezone.now()
    return now - service_td > dt_start

@register.filter
def util_get_min_time_str(t):
    result = ''
    if t is datetime.time.min:
        return 'мгновение'
    if t.hour:
        result += '{0} {1}'.format(t.hour, 'час' if t.hour == 1 else 'часа' if t.hour <= 4 else 'часов')
    if t.minute:
        result += '{0} {1}'.format(t.minute, 'минута' if t.minute == 1 else 'минуты' if t.minute <= 4 else 'минут')
    if not t.hour and t.second:
        result += '{0} {1}'.format(t.second, 'час' if t.second == 1 else 'часа' if t.second <= 4 else 'часов')
    return result

@register.filter
def util_contains_string(url, s):
    r = re.compile(s)
    return bool(r.match(url))

# Django make_list supports only strings, it`s terrible
@register.filter
def util_to_list(lst):
    return list(lst)

# Django make_list supports only strings, it`s terrible
@register.filter
def util_by_index(lst,i):
    return lst[i]

@register.filter
def util_is_comment_to_comment(com):
    return com.object_type == ContentType.objects.get(app_label='comment', model = 'comment')

@register.filter
def util_orders_to_json(orders):
    result = []
    for o in orders:
        to_add = {}
        to_add['time_start'] = o.start.time().strftime('%H:%M')
        to_add['time_end'] = o.end.time().strftime('%H:%M')
        if (isinstance(o.extra_data, dict) 
                and 'user' in o.extra_data
                and isinstance(o.extra_data['user'], User)):
            user = o.extra_data['user']
            to_add['user'] = {
                    'name': user.get_full_name(),
                    'phone_number': user.phone_number,
                    'account_id': user.account_id,
                    'email': user.email
                }
        result.append(to_add)
    return json.dumps(result)

@register.filter
def util_is_current_user_order(orders, user):
    for o in orders:
        if 'user' in o.extra_data and o.extra_data['user'] == user:
            return o.id
    return 0

@register.filter
def util_is_other_user_order(orders, user):
    for o in orders:
        if 'user' in o.extra_data and o.extra_data['user'] != user:
            return True
    return False

@register.filter
def util_get_single_item_orders_str(orders):
    if len(orders) == 1:
        return 'Заказал {0}'.format(orders[0].extra_data['user'].get_full_name())
    else:
        s = 'Заказано:'
        for o in orders[1:]:
            s += '<br/>[{0}-{1}] {2}'.format(o.start.strftime('%H:%M'), o.end.strftime('%H:%M'), o.extra_data['user'].get_full_name())
        return s

@register.filter
def util_get_field_verbose_name(model, field):
    if isinstance(field, str):
        f = model._meta.get_field(field)
        if f:
            return f.verbose_name
        else:
            return None
    else:
        return None

@register.filter
def util_get_form_field_verbose_name(form, field):
    if isinstance(form, ModelForm):
        return util_get_field_verbose_name(form._meta.model, field)
    else:
        return None

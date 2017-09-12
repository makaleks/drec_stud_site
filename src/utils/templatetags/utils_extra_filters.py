from django import template
import datetime

register = template.Library()

@register.filter
def util_by_key(dictionary, key):
    return dictionary.get(key)

@register.filter
def util_range(i):
    return range(i)

@register.filter
def util_add_user_info(lst, user):
    for day in lst:
        for machine in day['items'].values():
            i = 0
            column = machine['time']
            length = len(column)
            while i < length:
                u = column[i].get('user')
                if u and u == user:
                    if i != 0 and 'user' in column[i - 1]:
                        column[i - 1].update({'show_info': True})
                    if i != length - 1 and 'user' in column[i + 1]:
                        column[i + 1].update({'show_info': True})
                i+=1
            machine['time'] = column
    return lst

@register.filter
def util_is_started(time_start, service):
    service_td = datetime.datetime.combine(datetime.date.min, service.time_after_now) - datetime.datetime.min
    current_td = ((datetime.datetime.combine(
            datetime.date.min, datetime.datetime.now().time()) 
            - datetime.datetime.min) 
        - (datetime.datetime.combine(datetime.date.min, time_start)
            - datetime.datetime.min))
    return current_td <= service_td

from django.db import models
import datetime
import importlib
import re
import vk
from requests.exceptions import ReadTimeout


# Check that some field is unique for now
def check_unique(model, field_name, value):
    try:
        field = getattr(model, field_name)
        filter_dic = {field_name: value}
        num = model.objects.filter(**filter_dic).count()
        if num == 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def get_class_by_string(s):
    module_name, class_name = s.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def get_django_model_by_string(s):
    module_name, class_name = s.rsplit('.', 1)
    return get_class_by_string(module_name + '.models.' + class_name)

def get_id_by_url_vk(s):
    if not s:
        return None
    vk_api = vk.API(vk.Session())
    id_is_raw = re.compile(r"^(i|I)d[0-9]+$")
    if s[:7] == 'http://':
        s = s[7:]
    elif s[:8] == 'https://':
        s = s[8:]
    if s[:7] == 'vk.com/':
        s = s[7:]
    elif s[:9] == 'm.vk.com/':
        s = s[9:]
    if (s[:2] == 'id' or s[:2] == 'Id') and id_is_raw.match(tmp):
        s = s[2:]
    if s[-1] == '/':
        s = s[:-1]
    # You may set this different
    attempts = 3
    while attempts:
        try:
            s = vk_api.users.get(user_ids = s)
            return s[0]['uid']
        except BaseException as e:
            if not isinstance(e, ReadTimeout):
                return None
            else:
                attempts -= 1
                continue
    # Return the same is no internet connection
    return s
    

from django.db import models
import datetime
import importlib
import re
import vk
from requests.exceptions import ReadTimeout
from note.models import Question
from django.conf import settings


# Check that some field is unique for now
def check_unique(model, field_name, value):
    try:
        field = getattr(model, field_name)
        filter_dic = {field_name: value}
        existed = model.objects.filter(**filter_dic).first()
        if not existed:
            return None
        else:
            return existed
    except Exception as e:
        print(e)
        return None

def get_class_by_string(s):
    module_name, class_name = s.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def get_django_model_by_string(s):
    module_name, class_name = s.rsplit('.', 1)
    return get_class_by_string(module_name + '.models.' + class_name)

# You may set other number of request attempts
def get_id_by_url_vk(s, attempts = 3):
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
    if (s[:2] == 'id' or s[:2] == 'Id') and id_is_raw.match(s):
        s = s[2:]
    if s[-1] == '/':
        s = s[:-1]
    while attempts:
        try:
            s = vk_api.users.get(user_ids = s, v = 5.95, access_token = settings.SERVICE_KEY_VK)
            return s[0]['id']
        except BaseException as e:
            if not isinstance(e, ReadTimeout):
                return None
            else:
                attempts -= 1
                continue
    # Return the same is no internet connection
    return s

def util_get_new_question_num():
    num = Question.objects.filter(is_approved = False).count()
    started_questions = list(Question.objects.filter(is_approved = True))
    for q in started_questions:
        if not q.is_staff_answered():
            num += 1
    return num

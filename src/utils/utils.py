from django.db import models
import datetime
import importlib

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

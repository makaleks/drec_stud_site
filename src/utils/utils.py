from django.db import models
import datetime

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


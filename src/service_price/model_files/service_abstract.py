from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from service_item.models import ServiceItemAbstract

# Create your models here.

class ServicePriceAbstract(ServiceItemAbstract):
    default_price             = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена по-умолчанию за шаг времени', default = 0)
    late_cancel_multiplicator = models.FloatField(blank = False, null = False, validators = [MinValueValidator(0), MaxValueValidator(1)], default = 1.0, verbose_name = 'На сколько умножить при поздней отмене')
    # Returns {'date','datestr',
    #   'is_weekend': bool,
    #   'items': {'name': {
    #                       'is_open','price','rowspan',
    #                       'time':[TimetableInterval]
    #                     }
    #            }
    #   'timetable': [TimetableInterval]
    # }
    # or None if not working
    class Meta:
        abstract = True


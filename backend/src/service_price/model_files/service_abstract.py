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
    def get_discount(self, user):
        if not user.is_authenticated or not hasattr(self, 'discounts'):
            return 1.0
        min_fraction = 1.0
        # If 2+ discounts, find the best
        discounts = list(self.discounts.all())
        for d in discounts:
            if d.faculty.is_group_in_faculty(user.group_number) and d.discount < min_fraction:
                min_fraction = d.discount
        return min_fraction
    class Meta:
        abstract = True


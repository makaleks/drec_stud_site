from django.db import models

from service_item.models import OrderItemAbstract

# Return database filter to ServiceAbstract

def get_children_for_service_item():
    pass

# Create your models here.

class OrderPriceAbstract(OrderItemAbstract):
    payed       = models.PositiveSmallIntegerField(blank = False, null = False, verbose_name = 'Оплачено')
    # define your own 'item' field with related_name = 'orders'!
    # example:
    # item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    item        = None
    # define your own 'user' field with non-clashing related_name!
    # example:
    # user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    user        = None
    class Meta:
        abstract = True


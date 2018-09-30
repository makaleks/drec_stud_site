from django.db import models
from django.urls import reverse
from django.conf import settings

from service_base.utils import pk_to_url
from service_price.models import ServicePriceAbstract
from service_price.models import ItemPriceAbstract
from service_price.models import OrderPriceAbstract

# Create your models here.

class Washing(ServicePriceAbstract):
    # Placed not in ServiceBase to group children by type
    order      = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def get_absolute_url(self):
        return pk_to_url(Washing, self.pk, 'washing:washing_base', 'washing:washing_detail')
    def __str__(self):
        return 'Стиралка-{0}'.format(self.id)
    class Meta:
        verbose_name = 'Стиралка'
        verbose_name_plural = 'Стиралки'
        ordering            = ['order']


class WashingMachine(ItemPriceAbstract):
    service = models.ForeignKey(Washing, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Стиралка')
    class Meta:
        verbose_name = 'Машинка'
        verbose_name_plural = 'Машинки'
        ordering = ['order', 'price']


class Order(OrderPriceAbstract):
    item = models.ForeignKey(WashingMachine, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Машинка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'washing_orders', blank = False, null = False, verbose_name = 'Пользователь')
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-date_start', '-time_start']


from django.db import models

from service_item.models import ItemAbstract

# Return database filter to ServiceAbstract

def get_children_for_service_item():
    pass

# Create your models here.

class ItemPriceAbstract(ItemAbstract):
    # Remember to add 'price' field 
    # at Service.get_timetable()!
    price       = models.PositiveSmallIntegerField(blank = True, null = True, verbose_name = 'Цена за заказ', default = None)
    # define your own 'service' field with related_name = 'items'!
    # example:
    # service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    service = None

    def get_timetable_extra_data(self):
        return {'price': self.get_price()}
    def get_price(self):
        return self.price if self.price != None else self.service.default_price
    class Meta:
        abstract = True


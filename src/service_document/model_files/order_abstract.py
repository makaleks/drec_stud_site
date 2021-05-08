from django.db import models

from service_item.models import OrderItemAbstract

# Create your models here.

class OrderDocumentAbstract(OrderItemAbstract):
    is_approved = models.BooleanField(default = False, blank = False, null = False, verbose_name = 'Одобрено')
    title       = models.TextField(blank = True, null = True, verbose_name = 'Назначение заказа')
    # define your own 'item' field with related_name = 'orders'!
    # example:
    # item        = models.ForeignKey(Item, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Предмет сервиса')
    item        = None
    # define your own 'user' field with non-clashing related_name!
    # example:
    # user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Пользователь')
    user        = None
    @staticmethod
    def filter_queryset(queryset):
        query = super(OrderDocumentAbstract, OrderDocumentAbstract).filter_queryset(queryset).filter(is_approved = True)
        return query
    def is_good(self):
        if not self.is_approved:
            try:
                self.clean_time_limits()
            except Exception:
                return False
        return True
    class Meta:
        abstract = True

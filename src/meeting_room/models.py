from django.db import models
from django.conf import settings

from service_base.utils import pk_to_url
from service_document.models import ServiceDocumentAbstract, OrderDocumentAbstract
from service_item.models import ItemAbstract

# Create your models here.

class MeetingRoom(ServiceDocumentAbstract):
    # Placed not in ServiceBase to group children by type
    order      = models.PositiveSmallIntegerField(default = 0, blank = False, null = False, verbose_name = 'Порядок показа')
    def get_absolute_url(self):
        return pk_to_url(MeetingRoom, self.pk, 'meeting_room:room_base', 'meeting_room:room_detail')
    def __str__(self):
        return 'Комната-{0}'.format(self.id)
    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering            = ['order']


class MeetingRoomItem(ItemAbstract):
    service = models.ForeignKey(MeetingRoom, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    class Meta:
        verbose_name = 'Комната (item)'
        verbose_name_plural = 'Комнаты (item)'
        ordering = ['order']


class Order(OrderDocumentAbstract):
    item = models.ForeignKey(MeetingRoomItem, on_delete = models.CASCADE, related_name = 'orders', blank = False, null = False, verbose_name = 'Комната (item)')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'meeting_room_orders', blank = False, null = False, verbose_name = 'Пользователь')
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-date_start', '-time_start']


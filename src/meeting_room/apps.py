from django.apps import AppConfig
from django.db.models.signals import post_save


class MeetingRoomConfig(AppConfig):
    name = 'meeting_room'
    def ready(self):
        from meeting_room.models import MeetingRoom
        from meeting_room.signals import fill_single_item
        post_save.connect(fill_single_item, sender = MeetingRoom)

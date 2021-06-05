from .models import MeetingRoom, MeetingRoomItem

def fill_single_item(instance, **kwargs):
    if not instance.items.exists():
        print('Creating single item...')
        MeetingRoomItem(name = 'Комната {0}'.format(instance.name), service = instance).save()
        print('Done')


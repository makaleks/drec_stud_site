from .models import MenuEntry

def fill_default_menu_entry(sender, **kwargs):
    if not MenuEntry.objects.exists():
        print('Creating default set of menu entries...')
        MenuEntry.objects.bulk_create([
            MenuEntry(name = 'Новости', url = '/'),
            MenuEntry(name = 'Опросы', url = '/surveys/'),
            MenuEntry(name = 'Студсовет', url = '/notes/student_council/'),
            MenuEntry(name = 'Стиралка', url = '/services1/washing/'),
            MenuEntry(name = 'Другие сервисы', url = '/services/'),
            MenuEntry(name = 'FAQs', url = '/notes/'),
        ])
        print('Done')


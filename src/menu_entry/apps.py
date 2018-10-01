from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MenuEntryConfig(AppConfig):
    name = 'menu_entry'
    def ready(self):
        from menu_entry.signals import fill_default_menu_entry
        post_migrate.connect(fill_default_menu_entry, sender = self)

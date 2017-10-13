# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
# We don`t want so keep half of Users saved if a single (or more) error happens
from django.db import transaction
import json, argparse

from utils.utils import get_django_model_by_string

class Command(BaseCommand):
    help = 'Load new users using .txt file with JSON data'
    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'), help='Path to file')
    def handle(self, *args, **options):
        data = json.load(options['file'])
        self.stdout.write('{0}: {1}\n'.format(type(data), data))
        self.stdout.write('{0}: {1}\n'.format(type(settings.AUTH_USER_MODEL), settings.AUTH_USER_MODEL))
        user_class = get_django_model_by_string(settings.AUTH_USER_MODEL)
        try:
            with transaction.atomic():
                for d in data:
                    user = user_class(**d)
                    user.save()
        except BaseException as e:
            raise CommandError(str(e))
        self.stdout.write(self.style.SUCCESS('Done! Successfully written {0} users!'.format(len(data))))

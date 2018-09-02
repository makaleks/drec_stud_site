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
        parser.add_argument('allpossible', action='store_true')
    def handle(self, *args, **options):
        data = json.load(options['file'])
        self.stdout.write('{0}: {1}\n'.format(type(data), data))
        self.stdout.write('{0}: {1}\n'.format(type(settings.AUTH_USER_MODEL), settings.AUTH_USER_MODEL))
        user_class = get_django_model_by_string(settings.AUTH_USER_MODEL)
        user = None
        errors = []
        if options['allpossible']:
            for d in data:
                user = user_class(**d)
                try:
                    user.save()
                except BaseException as e:
                    if user:
                        errors.append(user.account_id)
                        self.stdout.write(self.style.ERROR('The following user caused error\n{0}'.format(user.get_all_data()))
                    else:
                        errors.append('ERR')
        else:
            try:
                with transaction.atomic():
                    for d in data:
                        user = user_class(**d)
                        user.save()
            except BaseException as e:
                if user:
                    self.stdout.write(self.style.ERROR('The following user caused error\n{0}'.format(user.get_all_data()))
                raise CommandError(str(e))
                self.stdout.write(self.style.SUCCESS('Done! Successfully written {0} users!{1}'.format(len(data), errors ? ' \nErrors:{0}'.format(errors):'')))

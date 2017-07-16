from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserInfo(models.Model):
    # refers to currently defined User model
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'info')
    account_url = models.CharField(max_length = 64, blank = False, null = False)
    patronymic_name = models.CharField(max_length = 32, blank = False, null = False)
    phone_number = models.CharField(max_length = 20, blank = False, null = False)
    

@receiver(post_save, sender = User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_user_info(sender, instance, **kwargs):
    instance.info.save()


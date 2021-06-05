from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from user.models import Faculty

# Create your models here.

class DiscountAbstract(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete = models.CASCADE, related_name = 'discounts', blank = False, null = False, verbose_name = 'Факультет')
    discount = models.FloatField(default = 1.0, blank = False, null = False, validators = [MinValueValidator(0.0), MaxValueValidator(1.0)], verbose_name = 'Доля от цены')
    # define your own 'service' field with related_name = 'items'!
    # example:
    # service     = models.ForeignKey(Service, on_delete = models.CASCADE, related_name = 'items', blank = False, null = False, verbose_name = 'Сервис')
    service = None
    class Meta:
        abstract = True


from django.db import models
from django.core.validators import FileExtensionValidator

from service_item.models import ServiceItemAbstract

# Create your models here.

class ServiceDocumentAbstract(ServiceItemAbstract):
    request_document = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf', 'odt', 'png', 'jpg', 'jpeg'])], blank = True, null = True, verbose_name = 'Служебка (doc/docx/pdf/odt/png/jpg/jpeg)')
    class Meta:
        abstract = True

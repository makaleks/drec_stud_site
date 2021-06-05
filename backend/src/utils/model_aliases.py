from django.db import models
from django.core.validators import FileExtensionValidator


class DefaultFileField(models.FileField):
    name = ''
    extentions = []
    # copy default ImageField and add some defaults
    def __init__(self, base_name = '', *args, **kwargs):
        extentions = self.extentions
        if not kwargs.get('validators'):
            kwargs['validators'] = [FileExtensionValidator(allowed_extensions=extentions)]
        name = self.name
        if base_name:
            name = base_name
        if not kwargs.get('verbose_name'):
            kwargs['verbose_name'] = '{0} ({1})'.format(name, ', '.join(extentions))
        super(DefaultFileField, self).__init__(*args, **kwargs)
    class Meta:
        proxy = True

class DefaultImageField(DefaultFileField):
    name = 'Изображение'
    extentions = ['jpg', 'jpeg', 'png', 'gif', 'svg']

class DefaultDocumentField(DefaultImageField):
    name = 'Документ'
    extentions = ['pdf', 'txt',
                'doc', 'docx', 'odt', 
                'xls', 'xlsx', 'ods',
                'ppt', 'pptx', 'odp',
            ] + DefaultImageField.extentions

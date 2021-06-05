from django.utils.safestring import mark_safe

class CustomBaseAdmin:
    def id_link(self, obj):
        return mark_safe(
            '<a href="{0}">{1}</a>'.format(
                obj.get_absolute_url(), str(obj.id))
            )

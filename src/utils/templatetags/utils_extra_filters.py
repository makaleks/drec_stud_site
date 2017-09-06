from django import template

register = template.Library()

@register.filter
def by_key(dictionary, key):
    return dictionary.get(key)

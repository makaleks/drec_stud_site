# coding: utf-8
from django.conf import settings

def custom_context(request):
    return {
        'notification': {
            'enabled': False,
            'text': 'Разработчик забыл установить текст :)',
            # Bootstrap-like colors
            # Possible: info (light blue), danger (red), dark (black),
            #           primary (blue), secondary (gray), success (green),
            #           warning (red-yellow), light (white)
            'type': 'light'
        },
        'pay_yandex': {
            'payment_text': settings.PAYMENT_TEXT_YANDEX,
            'success_redirect_url': settings.PAYMENT_SUCCESS_REDIRECT_YANDEX
        }
    }

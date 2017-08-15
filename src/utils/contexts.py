# coding: utf-8

def custom_context(request):
    return {
        'notification': {
            'enabled': False,
            'text': 'Разработчик забыл установить текст :)',
            # Possible: info (blue), danger (red), alert (yellow)
            'type': 'info'
        }
    }

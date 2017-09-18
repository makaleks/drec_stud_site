# coding: utf-8

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
        }
    }

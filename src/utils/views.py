from django.shortcuts import render

# Create your views here.

# 'exception' is the possible argument

# Bad request
def error_view_400(request, *args, **kwargs):
    response = render(request, 'core/error.html')
    response.status_code = 400
    return response

# Permission denied
def error_view_403(request, *args, **kwargs):
    response = render(request, 'core/error.html')
    response.status_code = 403
    return response

# Not found
def error_view_404(request, *args, **kwargs):
    response = render(request, 'core/error.html')
    response.status_code = 404
    return response

# Server error
def error_view_500(request, *args, **kwargs):
    response = render(request, 'core/error.html')
    response.status_code = 500
    return response

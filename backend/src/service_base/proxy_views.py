from django.http import HttpResponseRedirect, Http404
# For string manipulations
from os.path import dirname, basename

from .utils import order_to_pk

# Nice solution for nice URLs
# Let assume you have 3 models with id=[1,3,12]
#
# /service/washing/1   \
# /service/washing/3    - are bad
# /service/washing/12  /
#
# This view factory converts these URLs to
# /service/washing/1 
# /service/washing/2 
# /service/washing/3
# 
# The order depends on database ordering 
# (see [models.py] => [class Meta] => [ordering])
#
# Additional features (for this example)
# - max filter: /washing/100500/ => redirect /washing/3/
# - simple for single (one object only): /washing/ == /washing/1/
# - filter for many (more than 1 obj): /washing/ => redirect /washing/1/
#
# Examples:
# 1) urls.py:
# urlpatterns = [
#     path('<int:order>/', view_proxy_factory(Washing, 
#                 WashingDetailView.as_view()), name = 'washing_detail'),
#     path('', view_proxy_factory(Washing, 
#                 WashingDetailView.as_view()), name = 'washing_base'),
# ]
#
# 2) models.py:
# def get_absolute_url(self):
#     if Washing.objects.count() == 1:
#         return reverse('washing:washing_base')
#     else:
#         order = 1 + list(Washing.objects.all().values_list('pk', flat=True)).index(self.pk)
#         return reverse('washing:washing_detail', args=[order])


def view_proxy_factory(model, model_view):
    def view_proxy(request, order = 1, *args, **kwargs):
        path = request.path
        # The ending '/' is ignored by os.path
        path = path[:-1]
        max_order = model.objects.count()
        if max_order == 0:
            raise Http404
        if max_order < order:
            path = dirname(path) + '/' + str(max_order) + '/'
            return HttpResponseRedirect('{0}{1}'.format(path, '?{}'.format(request.GET.urlencode()) if request.GET else ''))
        if max_order > 1 and not basename(path).isdigit():
            path = path + '/1/'
            return HttpResponseRedirect(path)
        if basename(path) == '0':
            path = dirname(path) + '/1/'
            return HttpResponseRedirect(path)
        pk = order_to_pk(model, order)
        return model_view(request = request, pk = pk, *args, **kwargs)
    return view_proxy


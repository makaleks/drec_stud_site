from django.shortcuts import render

from service_item.views import ItemOrderingAbstractView

# Create your views here.

class ServiceDiscountAbstractView(ItemOrderingAbstractView):
    # Return min possible discount
    def get_context_data(self, **kwargs):
        context = super(ServiceDiscountAbstractView, self).get_context_data(**kwargs)
        obj = self.get_object()
        user = self.request.user
        context['discount'] = obj.get_discount(user)
        return context


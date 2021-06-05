from django.shortcuts import render

from service_item.views import ItemOrderingAbstractView

# Create your views here.

# This abstract class adds the ability to approve orders
# (context 'to_approve'
class OrderApprovingAbstractView(ItemOrderingAbstractView):
    def get_context_data(self, **kwargs):
        context = super(OrderApprovingAbstractView, self).get_context_data(**kwargs)
        not_approved = list(self.object.items.first().orders.all().filter(is_approved = False))
        to_approve = []
        for o in not_approved:
            if o.is_good():
                to_approve.append(o)
        context['to_approve'] = to_approve
        return context
    # Returns True if something happened
    def approve(self, request, order_model, *args, **kwargs):
        if request.user.is_staff:
            data = request.POST.dict()
            lst = []
            for k in data.keys():
                if k[:3] == 'id=':
                    lst.append(k[3:])
            orders = order_model.objects.all().filter(pk__in=lst)
            for o in orders:
                o.is_approved = True
                o.save()
            if orders:
                return True
        return False


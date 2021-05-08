from django.urls import reverse


def order_to_pk(model, order):
    if order < 1:
        return None
    lst = model.objects.all().values_list('pk', flat=True)
    if not lst or len(lst) < order:
        return None
    return lst[order - 1]

def pk_to_order(model, pk):
    lst = list(model.objects.all().values_list('pk', flat=True))
    if not pk in lst:
        return None
    return 1 + lst.index(pk)

def pk_to_url(model, pk, reverse_base, reverse_detail):
    if model.objects.count() == 1:
        return reverse(reverse_base)
    else:
        order = pk_to_order(model, pk)
        if order is None:
            return None
        return reverse(reverse_detail, args=[order])

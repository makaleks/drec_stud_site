'''
This module provides functions to keep a list sorted.
The elements of this list have own length, and the module ensures that elements don`t overflow each other.
Diagram:
[ . .|3 _ 5|6 _ _ 9|. . .|D _ F|]
Moreover, some kind of integrity assurance provided.
In addition, the type check is provided.
The module provides only insertion tools.
'''

from copy import copy

def sorted_insert(lst, obj_class, start_attr, end_attr, el):
    '''
    Inserts 'long' elements into list to keep it sorted.
    The 'length' of the element is defined by comparable element attributes (``start_attr``, ``end_attr``).
    The result is saved to argument and returned.
    All checks included. Some integrity assurance included.
    The used model is '[start, end)'

    :var lst: the list, where the result should be saved
    :var obj_class: the class of ``el`` and elements of ``lst``
    :var start_attr: the name of the 'start' attribute, used in comparison
    :var end_attr: the name of the 'end' attribute, used in comparison
    :var el: the element to insert into a sorted list
    :type lst: list
    :type obj_class: class
    :type start_attr: str
    :type end_attr: str
    :el: obj_class
    '''
    if not (isinstance(lst, list) and all(isinstance(l, obj_class) for l in lst)):
        raise TypeError('lst({0}) must be list of {1}'.format(lst.__class__.__name__, str(obj_class)))
    elif not all(isinstance(a, str) for a in [start_attr, end_attr]):
        raise TypeError('start_attr({0}) and end_attr({1}) must be str'.format(start_attr.__class__.__name__, end_attr.__class__.__name__))
    if isinstance(el, obj_class):
        if getattr(el, start_attr) > getattr(el, end_attr):
            raise TypeError('element {0} must have start_attr({1}) <= end_attr({2})'.format(str(el), str(getattr(el, start_attr)), str(getattr(el, end_attr))))
        not_done = True
        for i in range(0, len(lst)):
            if getattr(el, end_attr) <= getattr(lst[i], start_attr):
                if i != 0 and getattr(el, start_attr) < getattr(lst[i - 1], end_attr):
                    raise ValueError('Can`t insert {0} between {1} and {2}'.format(str(el), str(lst[i - 1]), str(lst[i])))
                not_done = False
                lst.insert(i, el)
                break
        if not_done:
            lst.append(el)
    elif isinstance(el, list) and all(isinstance(e, obj_class) for e in el):
        # The copy is required for the case that some element is overflowed
        lst_copy = copy(lst)
        for e in el:
            sorted_insert(lst_copy, obj_class, start_attr, end_attr, e)
        lst.clear()
        lst.extend(lst_copy)
    else:
        raise TypeError('el({0}) must be {1} or a list of them'.format(el.__class__.__name__, str(obj_class)))

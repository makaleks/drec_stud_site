
def long_sorted_search(lst, el_obj_class, el_start_attr, el_end_attr, el, lst_obj_class = None, lst_start_attr = None, lst_end_attr = None):
    '''
    Searches 'long' elements in sorted list using binary search.
    The 'length' of the element is defined by comparable element attributes (``el_start_attr``, ``el_end_attr``).
    The list elements must not overflow each other.
    All other checks included.
    The used model is '[start, end)'

    :var lst: the list, where the result should be saved
    :var el_obj_class: the class of ``el``
    :var el_start_attr: the name of the element 'start' attribute, used in comparison
    :var el_end_attr: the name of the element 'end' attribute, used in comparison
    :var el: the element to insert into a sorted list
    :var lst_obj_class: optional (default=el_obj_class), the class of elements of ``lst``
    :var lst_start_attr: optional (default=el_start_attr), the name of the list object 'start' attribute
    :var lst_end_attr: optional (default=el_end_attr), the name of the list object 'end' attribute
    :type lst: list
    :type el_obj_class: class
    :type el_start_attr: str
    :type el_end_attr: str
    :type el: el_obj_class
    :type lst_obj_class: class
    :type lst_start_attr: str
    :type lst_end_attr: str
    :rtype: list (of lst_obj_class)
    '''
    if lst_obj_class is None:
        lst_obj_class = el_obj_class
    if not (isinstance(lst, list) and all(isinstance(l, lst_obj_class) for l in lst)):
        raise TypeError('lst({0}) must be list of {1}'.format(lst.__class__.__name__, str(lst_obj_class)))
    elif not all(isinstance(a, str) for a in [el_start_attr, el_end_attr]):
        raise TypeError('el_start_attr({0}) and el_end_attr({1}) must be str'.format(el_start_attr.__class__.__name__, el_end_attr.__class__.__name__))
    elif not isinstance(el, el_obj_class):
        raise TypeError('el({0}) must be {1}'.format(el.__class__.__name__, str(el_obj_class)))
    elif getattr(el, el_start_attr) > getattr(el, el_end_attr):
        raise TypeError('element {0} must have el_start_attr({1}) <= el_end_attr({2})'.format(str(el), str(getattr(el, el_start_attr)), str(getattr(el, el_end_attr))))
    if lst_start_attr is None and lst_end_attr is None:
        lst_start_attr = el_start_attr
        lst_end_attr = el_end_attr
    elif not all(isinstance(a, str) for a in [lst_start_attr, lst_end_attr]):
        raise TypeError('lst_start_attr({0}) and lst_end_attr({1}) must be str'.format(lst_start_attr.__class__.__name__, lst_end_attr.__class__.__name__))
    if not lst:
        return []
    if getattr(lst[0], lst_start_attr) >= getattr(el, el_end_attr) or getattr(lst[-1], lst_end_attr) <= getattr(el, el_start_attr):
        return []
    start_i = 0
    end_i = len(lst)
    result = []
    found = False
    # Binary search of some list elements, that correspond to 'el'
    while start_i != end_i:
        middle = (start_i + end_i) // 2
        #0...|lst-el|.....N
        #0........#el#...N
        if (getattr(lst[middle], lst_start_attr) <= getattr(el, el_start_attr) 
                and getattr(el, el_start_attr) < getattr(lst[middle], lst_end_attr)):
            start_i = end_i = middle
            found = True
            break
        #0...|lst-el|.....N
        #0..#el#..........N
        if (getattr(lst[middle], lst_start_attr) < getattr(el, el_end_attr) 
                and getattr(el, el_end_attr) <= getattr(lst[middle], lst_end_attr)):
            start_i = end_i = middle
            found = True
            break
        #0...|lst-el|.....N
        #0.#longer elem#..N
        if (getattr(el, el_start_attr) < getattr(lst[middle], lst_start_attr) 
                and getattr(lst[middle], lst_end_attr) < getattr(el, el_end_attr)):
            start_i = end_i = middle
            found = True
            break
        # Prepare next search iteration
        if getattr(el, el_end_attr) <= getattr(lst[middle], lst_start_attr):
            if end_i - start_i == 1:
                # movement has to be forces
                # for middle = (start_i + end_i) // 2
                end_i -= 1
            else:
                end_i = middle
        else:
            if end_i - start_i == 1:
                # movement has to be forces
                # for middle = (start_i + end_i) // 2
                start_i += 1
            else:
                start_i = middle
    if not found:
        return []
    # Insert first found
    result.append(lst[start_i])
    # Find possible before, go left
    #0...|inter|.....N
    #0...#ord#ord#...N
    i = start_i
    if i != 0 and getattr(lst[i - 1], lst_end_attr) > getattr(el, el_start_attr):
        while i != 0:
            if getattr(lst[i - 1], lst_end_attr) <= getattr(el, el_start_attr):
                break
            result.insert(0, lst[i - 1])
            i -= 1
    # Find possible after, go right
    #0....|inter|....N
    #0..#ord#ord#....N
    i = start_i
    if i != len(lst) - 1 and getattr(lst[i + 1], lst_start_attr) < getattr(el, el_end_attr):
        while i != len(lst) - 1:
            if getattr(lst[i + 1], lst_start_attr) >= getattr(el, el_end_attr):
                break
            result.append(lst[i + 1])
            i += 1
    return result


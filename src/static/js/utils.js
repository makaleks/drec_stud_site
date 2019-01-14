;
function util_add_handler(elem, event_str, handler) {
    if (!elem)
        return;
    if (elem.addEventListener)
        elem.addEventListener(event_str, handler);
    else
        elem.attachEvent('on' + event_str, handler);
}
function util_dispatch_event(elem, event_str) {
    var event; // The custom event that will be created

    if (document.createEvent) {
        event = document.createEvent("HTMLEvents");
        event.initEvent(event_str, true, true);
    } 
    else {
        event = document.createEventObject();
        event.eventType = event_str;
    }
    event.eventName = event_str;

    if (document.createEvent) {
        elem.dispatchEvent(event);
    } 
    else {
        elem.fireEvent("on" + event.eventType, event);
    }
}
function util_has_class(elem, class_name) {
    return (' ' + elem.className + ' ').indexOf(' ' + class_name + ' ') > -1;
}
function util_add_class(elem, class_name) {
    if (util_has_class(elem, class_name))
        return
    var existing_classes_normalized = ' ' + elem.className + ' ';
    var new_class_normalized = ' ' + class_name + ' ';
    if(existing_classes_normalized.indexOf(new_class_normalized) == -1) {
        elem.className += ' ' + class_name;
    }
}
function util_remove_class(elem, class_name) {
    if (util_has_class(elem, class_name)) {
        // \s is a whitespace
        // second replace is required for case 'target other' => ' other'
        elem.className = elem.className.replace(new RegExp('(\\s|^)'+class_name+'(\\s|$)'),' ').replace(/^\s+|\s+$/g, '');
    }
}

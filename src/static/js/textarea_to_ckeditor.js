;
// Remember to add 
// <script src='{{ STATIC_URL }}settings/ckeditor_settings.js'></script>
// to have 'options' accessable

function textarea_to_ckeditor() {
    areas = document.getElementsByTagName('textarea');
    var l = null;
    for (var i = 0; i < areas.length; i++) {
        if(areas[i].parentNode) {
            l = areas[i].parentNode.getElementsByTagName('label')[0];
            if (l)
                l.style.float = 'none';
        }
        CKEDITOR.replace(areas[i], options);
    }
};

util_add_handler(window, 'load', textarea_to_ckeditor);

;
// Register checkboxes to show preview
// see javascript pattern 'module'
var PRICE_PREVIEW = (function() {
    var registered_buttons = [];
    var preview_node = null;
    var result_node = null;
    var bool_func = null;
    function bool_checkbox(elem) {
        return elem.checked ? true : false;
    }
    function updateTexts() {
        // note: classList is supported just in IE10+
        if (!(preview_node && result_node && bool_checkbox))
            return;
        var total = 0;
        var groups = {};
        var len = 0;
        for (var i = 0; i < registered_buttons.length; i++) {
            // in JS there is no difference in meaning of perfomance
            // 'var' is a directive for parser, not a command for run-time
            e = registered_buttons[i];
            // error on getAttribute returns null
            // error on parseInt returns NaN
            if (e.getAttribute('data-timestart') 
                && e.getAttribute('data-timeend')) {
                var price = parseInt(e.getAttribute('data-price'), 10);
                if (bool_checkbox(e)) {
                    if (!isNaN(price))
                        total += price;
                    var name = e.getAttribute('data-item');
                    if (!(name in groups))
                        groups[name] = [e];
                    else
                        groups[name].push(e);
                    len++;
                }
            }
        }
        if (len) {
            preview_node.innerHTML = '<p>Итого интервалов: ' + (total > 0 ? '+' : '-') + len + (total ? (' за <span style="white-space:nowrap;">' + (total > 0 ? '-' : '+') + Math.abs(total) + ' руб.</span>') : '') + ' <a href="#finaltext">К оплате</a></p>';
            result_node.innerHTML = 'Выбрано интервалов: ' + len;
            if (total)
                result_node.innerHTML += '<br />Итого ' + (total > 0 ? 'нужно оплатить' : 'будет возвращено') + ': <span style="white-space:nowrap;">' + Math.abs(total) + ' руб.</span>';
            var table = '<br/><br/>Подробно:<br/><table style="border:none;">';
            for (var name in groups) {
                table += '<tr><td style="vertical-align:top;padding:10px;border:none;width:auto;"><span style="white-space:nowrap;">' + name + '</span></td><td style="padding:10px;border:none;width:auto;text-align:left;">';
                for (var i = 0; i < groups[name].length; i++) {
                    var time_start = groups[name][i].getAttribute('data-timestart');
                    var time_end = groups[name][i].getAttribute('data-timeend');
                    var price = groups[name][i].getAttribute('data-price');
                    var price_str = '';
                    if (price && price != '0')
                        price_str = ', ' + (price > 0 ? '-' : '+') + Math.abs(price) + ' руб.';
                    if (i != 0)
                        table += ', ';
                    table += '<span style="white-space:nowrap;">[' + time_start + '-' + time_end + price_str + ']</span>';
                }
                table += '</td></tr>';
            }
            result_node.innerHTML += table;
            util_remove_class(preview_node, 'hidden');
        }
        else {
            result_node.innerHTML = 'Вы ничего не выбрали';
            util_add_class(preview_node, 'hidden');
        }
    }
    function checkbox_callback() {
        updateTexts();
    }
    return {
        registerCheckboxes: function(inputRootId, previewId, resultId) {
            root = document.getElementById(inputRootId);
            inputs = root.querySelectorAll('input[type=checkbox]');
            for (var i = 0; i < inputs.length; i++) {
                util_add_handler(inputs[i], 'change', checkbox_callback);
                registered_buttons.push(inputs[i]);
            }
            preview_node = document.getElementById(previewId);
            result_node = document.getElementById(resultId);
            bool_func = bool_checkbox;
        },
        updateTexts: updateTexts
    }
})();

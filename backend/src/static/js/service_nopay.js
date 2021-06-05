window.addEventListener('load', function() {
    var preview = document.querySelector('#pretext'),
        finalview = document.querySelector('#finaltext'),
        currentprice = 0,
        add = 0,
        inputs = document.querySelector('#service').querySelectorAll('input[type=checkbox]');

    for (var item of inputs) {
        item.addEventListener('change', function() {
            if (this.checked) {
                add++;
            } else {
                add--;
            }
            if (add > 0) {
                preview.innerHTML = 'Выбрано: ' + add + 'интервалов <a href="#finaltext">К подтверждению</a>';
                document.querySelector('#preresult').classList.remove('hidden');
                finalview.innerHTML = 'Выбрано интервалов: ' + add;
            } else {
                finalview.innerHTML = 'Вы ничего не выбрали';
                document.querySelector('#preresult').classList.add('hidden');
            }
        });
    }
    document.querySelector('#finalcancel').addEventListener('click', function() {
        addwash = 0;
        removewash = 0;
        currentprice = 0;
        for (var item of inputs) {
            item.checked = false;
        };
        finalview.innerHTML = 'Вы ничего не выбрали';
        document.querySelector('#preresult').classList.add('hidden');
    });
});

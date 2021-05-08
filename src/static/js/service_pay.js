window.addEventListener('load', function() {
    var preview = document.querySelector('#pretext'),
        finalview = document.querySelector('#finaltext'),
        currentprice = 0,
        price = 0,
        addwash = 0,
        removewash = 0,
        inputs = document.querySelector('#service').querySelectorAll('input[type=checkbox]');

    for (var item of inputs) {
        item.addEventListener('change', function() {
            price = parseInt(this.getAttribute('data-price'), 10);
            if (this.checked) {
                if (price > 0) {
                    addwash++;
                } else {
                    removewash++;
                }
                currentprice += price;
            } else {
                if (price > 0) {
                    addwash--;
                } else {
                    removewash--;
                }
                currentprice -= price;
            }
            if (addwash > 0) {
                preview.innerHTML = ((addwash > 0) ? ('Выбрано: ' + addwash) : '') + ' <a href="#finaltext">К подтверждению</a>';
                document.querySelector('#preresult').classList.remove('hidden');
                finalview.innerHTML = 'Выбрано интервалов: ' + addwash;
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

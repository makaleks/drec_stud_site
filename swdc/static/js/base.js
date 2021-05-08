(function() {
    var bottom = document.querySelector('#bottom_menu'),
        top = document.querySelector('#top');
    document.querySelector("#showside").addEventListener('change',
        function(){
            if(this.checked) document.body.style.overflow = "hidden";
            else document.body.style.overflow = "auto";
        }, false);
    if (getComputedStyle(bottom).display !== 'none') {
        window.addEventListener('scroll', scrollPage, false);
        document.body.addEventListener('scroll', scrollPage, false);
        var height = bottom.getBoundingClientRect().height;
    }
    function scrollPage() {
        if (top.getBoundingClientRect().bottom <= height) {
            bottom.classList.add('sticky');
            top.style.paddingBottom = height + 'px';
        } else {
            bottom.classList.remove('sticky');
            top.style.paddingBottom = 0 + 'px';
        }
    }
})();
function showuserinfo(name, vkid, number, email) {
    var content = document.querySelector('#modal_userinfo_content');
    while (content.firstChild)
        content.removeChild(content.firstChild);
    var details_added = false;
    if (name) {
        var el_name = document.createElement('h3');
        el_name.innerText = name;
        content.appendChild(el_name);
    }
    if (number) {
        var el_number = document.createElement('a');
        el_number.innerText = 'Позвонить: ' + number;
        el_number.href = 'tel:' + number;
        content.appendChild(el_number);
        details_added = true;
    }
    if (vkid) {
        if (details_added)
            content.appendChild(document.createElement('br'));
        var el_vkid = document.createElement('a');
        el_vkid.innerText = 'Написать в ВК vk.com/id' + vkid;
        el_vkid.href = 'https://vk.me/id' + vkid;
        content.appendChild(el_vkid);
        details_added = true;
    }
    if (email) {
        if (details_added)
            content.appendChild(document.createElement('br'));
        var el_email = document.createElement('a');
        el_email.innerText = 'Написать: ' + email;
        el_email.href = 'mailto:' + email;
        content.appendChild(el_email);
        details_added = true;
    }
};

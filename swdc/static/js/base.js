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
    var username = document.querySelector('#userinfo_name'),
        uservkid = document.querySelector('#userinfo_vkid'),
        usernumber = document.querySelector('#userinfo_number'),
        useremail = document.querySelector('#userinfo_email');
    usernumber.classList.add('hidden');
    uservkid.classList.add('hidden');
    useremail.classList.add('hidden');
    username.innerText = name;
    if (number !== null) {
        usernumber.innerText = 'Позвонить: ' + number;
        usernumber.href = 'tel:' + number;
        usernumber.classList.remove('hidden');
    }
    if (vkid !== null) {
        uservkid.innerText = 'Написать в ВК vk.com/id' + vkid;
        uservkid.href = 'https://vk.me/id' + vkid;
        uservkid.classList.remove('hidden');
    }
    if (email !== null) {
        useremail.innerText = 'Написать: ' + email;
        useremail.href = 'mailto:' + email;
        useremail.classList.remove('hidden');
    }
};

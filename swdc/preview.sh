sed -e '/<!--{% block content %}-->/{ r core/index.html' -e 'd}' core/base.html > preview/index.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/index.html
sed -i 's/{%.*%}//' preview/index.html
sed -e '/<!--{% block content %}-->/{ r core/services/washing.html' -e 'd}' core/base.html > preview/washing.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/washing.html
sed -i 's/{%.*%}//' preview/washing.html

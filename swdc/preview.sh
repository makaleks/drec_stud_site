sed -e '1!N;/<!--{% block content %}\n *{% endblock %}-->/{ r core/index.html' -e 'd}' core/base.html > preview/index.html
sed -i 's/{{ STATIC_URL }}/..\/static\//' preview/index.html
sed -i 's/{%.*%}//' preview/index.html

sed -e '/<!--{% block content %}-->/{ r core/index.html' -e 'd}' core/base.html > preview/index.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/index.html
sed -i 's/{%.*%}//' preview/index.html
sed -e '/<!--{% block content %}-->/{ r core/services/index.html' -e 'd}' core/base.html > preview/services.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/services.html
sed -i 's/{%.*%}//' preview/services.html
sed -e '/<!--{% block content %}-->/{ r core/services/washing.html' -e 'd}' core/base.html > preview/washing.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/washing.html
sed -i 's/{%.*%}//' preview/washing.html
sed -e '/<!--{% block content %}-->/{ r core/survey.html' -e 'd}' core/base.html > preview/survey.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/survey.html
sed -i 's/{%.*%}//' preview/survey.html
sed -e '/<!--{% block content %}-->/{ r core/surveys_list.html' -e 'd}' core/base.html > preview/survey_list.html
sed -i 's/{{ STATIC_URL }}/..\/static/' preview/survey_list.html
sed -i 's/{%.*%}//' preview/survey_list.html
cd static
cat main.css index.css surveys.css services.css washing.css > content.css
cd ../
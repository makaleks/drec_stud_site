mkdir -p preview
mkdir -p preview/services
for FILE in index survey surveys_list note; do
    echo $FILE;
    awk -v FILE="$FILE" '
    {
        if($0 ~ /{% [ _a-z]* %}/)
        {
            if($0 ~ /{% block head_extras %}/)
            {
                i=0;
                while ( getline x < ("core/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block head_extras %}/){i=1;}
                };
                close("core/"FILE".html");
            }
            else if($0 ~ /{% block content %}/)
            {
                i=0;
                while ( getline x < ("core/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block content %}/){i=1;}
                };
                close("core/"FILE".html");
            }
            else if($0 ~ /{% block body_extras %}/)
            {
                i=0;
                while ( getline x < ("core/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block body_extras %}/){i=1;}
                };
                close("core/"FILE".html");
            }
            else if(!($0 ~ /{% endblock %}/)) {print $0;}
        }
        else {print $0;}
    }' core/base.html > preview/$FILE.html;
    sed -i "s/{{ STATIC_URL }}/..\/static/" preview/$FILE.html;
    sed -i "s/{[\{\%] [ _\.a-z]* [\%\}]}//g" preview/$FILE.html;
done
for FILE in index washing; do
    echo "services/$FILE";
    awk -v FILE="$FILE" '
    {
        if($0 ~ /{% [ _a-z]* %}/)
        {
            if(/{% block head_extras %}/)
            {
                i=0;
                while ( getline x < ("core/services/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block head_extras %}/){i=1;}
                };
                close("core/services/"FILE".html");
            };
            if(/{% block content %}/)
            {
                i=0;
                while ( getline x < ("core/services/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block content %}/){i=1;}
                };
                close("core/services/"FILE".html");
            };
            if(/{% block body_extras %}/)
            {
                i=0;
                while ( getline x < ("core/services/"FILE".html") > 0 )
                {
                    if(x ~ /{% endblock %}/){i=2;}
                    if(i == 1){print x;}
                    if(x ~ /{% block body_extras %}/){i=1;}
                };
                close("core/services/"FILE".html");
            };
        }
        else {print $0;}
    }' core/base.html > preview/services/$FILE.html;
    sed -i "s/{{ STATIC_URL }}/..\/..\/static/" preview/services/$FILE.html;
    sed -i "s/{[\{\%] [ _\.a-z]* [\%\}]}//g" preview/services/$FILE.html;
done
sh build.sh

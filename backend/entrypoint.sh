#!/bin/bash
set -x
set -o pipefail
cd src/
chmod +x manage.py
./manage.py makemigrations
./manage.py migrate
# Статику потом заберет nginx через volume mount
./manage.py collectstatic
cd ..


gunicorn -b 0.0.0.0:8080 -w 4 --pythonpath /app/src drec_stud_site.wsgi:application

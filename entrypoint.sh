#!/bin/bash
set -x
set -o pipefail
cd src/
sleep 5
chmod +x manage.py
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic
cd ..
chmod +x pgdump_helper.py
#./scripts/pgdump_helper.py --restore -f "db_backup.sql"


gunicorn -b 0.0.0.0:8080 -w 4 --pythonpath /app/src drec_stud_site.wsgi:application

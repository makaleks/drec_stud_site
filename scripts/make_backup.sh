#!/bin/bash
set +x
set -o pipefail
postgres_container=$(docker-compose ps -q postgres)
BACKUP_DIR=${BACKUP_PATH:-$(pwd)/backups}
docker exec "$postgres_container" pg_dump -c -U drec_stud_site_admin drec_stud_site\
 > "$BACKUP_DIR/stirka_postgres_dump_$(date +%d-%m-%Y"_"%H_%M_%S).sql"
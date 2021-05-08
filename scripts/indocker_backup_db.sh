#!/bin/bash
BACKUP_DIR=${BACKUP_PATH:-/backups}
BACKUP_DATE=$(date +%d-%m-%Y"_"%H_%M_%S)
BACKUP_INTERVAL=3600

echo "Performing backup on date $BACKUP_DATE"
PGPASSWORD=postgres pg_dump -c -h postgres -U postgres drec_stud_site\
 > "$BACKUP_DIR/stirka_postgres_dump_$BACKUP_DATE.sql"

echo "Done backuping, sleeping $BACKUP_INTERVAL seconds"
sleep $BACKUP_INTERVAL
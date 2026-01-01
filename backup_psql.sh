#!/bin/bash

# CONFIG
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="postgres"
PG_DB="nyaya_ai_db"

# Backup directory
BACKUP_DIR=${1:-"$PWD/backup_files/"}
LOG_FILE="$BACKUP_DIR/backup.log"

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
SQL_FILE="${PG_DB}_${DATE}.sql"
ARCHIVE_FILE="${PG_DB}_backup_${DATE}.tar.xz"

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log "Starting backup for database: $PG_DB"

# ------------------------------------------
# 1. Dump PostgreSQL using INSERT statements
# ------------------------------------------
PGPASSWORD="postgres" pg_dump \
    -h "$PG_HOST" \
    -p "$PG_PORT" \
    -U "$PG_USER" \
    --if-exists \
    --create \
    --clean \
    --no-comments \
    "$PG_DB" > "$BACKUP_DIR/$SQL_FILE"


if [ $? -ne 0 ]; then
    log "❌ pg_dump failed!"
    rm -f "$BACKUP_DIR/$SQL_FILE"
    exit 1
fi


# ------------------------------------------
# 3. Compress into tar.xz
# ------------------------------------------
tar -cJf "$BACKUP_DIR/$ARCHIVE_FILE" -C "$BACKUP_DIR" "$SQL_FILE"

if [ $? -ne 0 ]; then
    log "❌ Compression failed!"
    rm -f "$BACKUP_DIR/$SQL_FILE"
    exit 1
fi

# Remove raw SQL file
rm -f "$BACKUP_DIR/$SQL_FILE"

log "✅ Backup created: $ARCHIVE_FILE"

KEEP_BACKUP_CNT=5
# ------------------------------------------
# 4. Keep ONLY last $KEEP_BACKUP_CNT backups (auto-delete older)
# ------------------------------------------
cd "$BACKUP_DIR"

COUNT=$(ls -1 *.tar.xz 2>/dev/null | wc -l)

if [ $COUNT -gt $KEEP_BACKUP_CNT ]; then
    REMOVE_COUNT=$((COUNT-5))
    OLD_FILES=$(ls -1t *.tar.xz | tail -n $REMOVE_COUNT)

    for file in $OLD_FILES; do
        log "🗑 Removing old backup: $file"
        rm -f "$file"
    done
fi

log "Cleanup complete. Total backups kept: $KEEP_BACKUP_CNT"

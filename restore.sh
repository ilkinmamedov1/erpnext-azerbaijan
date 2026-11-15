#!/usr/bin/env bash
# ==============================================================================
# 🇦🇿 ERPNext Azərbaycan - Tam Bərpa Skripti (Full Restore)
# ==============================================================================
# Bu skript ./backups/ qovluğundakı backup fayllarını:
# - Verilənlər bazası (*.sql.gz)
# - Sayt konfiqurasiyası (*.json)
# - İctimai fayllar (*-files.tar)
# - Gizli fayllar (*-private-files.tar)
# ERPNext sisteminə bərpa edir.
# ==============================================================================

set -e

# .env oxu
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs -d '\n' 2>/dev/null || true)
fi

SITE_NAME=${SITE_NAME:-frontend}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-admin}

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=================================================================${NC}"
echo -e "${CYAN}   🔄  ERPNEXT TAM BƏRPA (RESTORE) - ${SITE_NAME}               ${NC}"
echo -e "${CYAN}=================================================================${NC}"

if ! docker ps --format '{{.Names}}' | grep -q "^erp_az_backend$"; then
    echo -e "${RED}XƏTA: erp_az_backend konteyneri işləmir.${NC}"
    echo -e "Zəhmət olmasa əvvəlcə sistemi işə salın: ${CYAN}docker compose up -d${NC}"
    exit 1
fi

# ./backups qovluğundakı SQL nüsxələrini yoxla
SQL_FILES=(./backups/*database*.sql.gz ./backups/*.sql.gz)
VALID_SQL=""

for f in "${SQL_FILES[@]}"; do
    if [ -f "$f" ]; then
        VALID_SQL="$f"
        break
    fi
done

if [ -z "$VALID_SQL" ]; then
    echo -e "\n${YELLOW}ℹ️  Məlumat: ./backups/ qovluğunda heç bir .sql.gz faylı aşkar edilmədi.${NC}"
    echo -e "Bərpa etmək üçün mövcud backup fayllarınızı ${CYAN}./backups/${NC} qovluğuna qoyun:"
    echo -e "   1. ${GREEN}*-database.sql.gz${NC} (Mütləq - verilənlər bazası)"
    echo -e "   2. ${GREEN}*-site_config_backup.json${NC} (İstəyə görə - açarlar)"
    echo -e "   3. ${GREEN}*-files.tar${NC} (İstəyə görə - yüklənmiş açıq fayllar)"
    echo -e "   4. ${GREEN}*-private-files.tar${NC} (İstəyə görə - gizli fayllar)"
    echo -e "\nFaylları yerləşdirdikdən sonra bu skripti yenidən icra edin: ${CYAN}./restore.sh${NC}"
    exit 0
fi

# Ən son backup faylını tap
LATEST_SQL=$(ls -t ./backups/*database*.sql.gz ./backups/*.sql.gz 2>/dev/null | head -n 1)
SQL_BASENAME=$(basename "$LATEST_SQL")

# Fayl adının prefiksi əsasında files.tar və private-files.tar yoxla
BASE_PREFIX="${LATEST_SQL%-database.sql.gz}"
PUBLIC_TAR="${BASE_PREFIX}-files.tar"
PRIVATE_TAR="${BASE_PREFIX}-private-files.tar"

EXTRA_ARGS=""
if [ -f "$PUBLIC_TAR" ]; then
    PUB_NAME=$(basename "$PUBLIC_TAR")
    EXTRA_ARGS="$EXTRA_ARGS --with-public-files /backups/$PUB_NAME"
fi

if [ -f "$PRIVATE_TAR" ]; then
    PRIV_NAME=$(basename "$PRIVATE_TAR")
    EXTRA_ARGS="$EXTRA_ARGS --with-private-files /backups/$PRIV_NAME"
fi

echo -e "\n${YELLOW}>>> Aşkar edilən backup faylları:${NC}"
echo -e "   SQL Baza:     ${GREEN}${SQL_BASENAME}${NC}"
if [ -n "$PUB_NAME" ]; then echo -e "   Açıq fayllar: ${GREEN}${PUB_NAME}${NC}"; fi
if [ -n "$PRIV_NAME" ]; then echo -e "   Gizli fayllar: ${GREEN}${PRIV_NAME}${NC}"; fi

if [ -t 0 ]; then
    read -p "DİQQƏT: Bu əməliyyat cari saytın məlumatlarını backup ilə əvəzləyəcək. Davam edilsin? (b/x): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[bByY] ]]; then
        echo -e "${YELLOW}Əməliyyat ləğv edildi.${NC}"
        exit 0
    fi
fi

echo -e "\n${YELLOW}>>> [1/2] Sayt bazası və fayllar bərpa edilir...${NC}"
docker compose exec -T backend bench --site "${SITE_NAME}" restore "/backups/${SQL_BASENAME}" --mariadb-root-username=root --mariadb-root-password="${DB_ROOT_PASSWORD}" $EXTRA_ARGS

echo -e "\n${YELLOW}>>> [2/2] Miqrasiya icra olunur (bench migrate)...${NC}"
docker compose exec -T backend bench --site "${SITE_NAME}" migrate

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}✓ ERPNEXT SAYTI VƏ VERİLƏNLƏR BAZASI UĞURLA BƏRPA EDİLDİ!${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "🔗 Veb Ünvan: ${CYAN}http://localhost:${HTTP_PORT:-8080}${NC}\n"

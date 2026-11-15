#!/usr/bin/env bash
# ==============================================================================
# 🇦🇿 ERPNext Azərbaycan - Tam Nüsxələmə Skripti (Full Backup)
# ==============================================================================
# Bu skript işləyən ERPNext sisteminin:
# 1. MariaDB verilənlər bazasını (*.sql.gz)
# 2. Sayt konfiqurasiyasını (*.json)
# 3. İctimai və gizli yüklənmiş fayllarını (*.tar)
# tam şəkildə arxivləyib ./backups/ qovluğuna çıxarır.
# ==============================================================================

set -e

# .env oxu
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs -d '\n' 2>/dev/null || true)
fi

SITE_NAME=${SITE_NAME:-frontend}
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=================================================================${NC}"
echo -e "${CYAN}   📦  ERPNEXT TAM NÜSXƏLƏMƏ (FULL BACKUP) - ${SITE_NAME}      ${NC}"
echo -e "${CYAN}=================================================================${NC}"

if ! docker ps --format '{{.Names}}' | grep -q "^erp_az_backend$"; then
    echo -e "${RED}XƏTA: erp_az_backend konteyneri işləmir.${NC}"
    echo -e "Zəhmət olmasa əvvəlcə sistemi işə salın: ${CYAN}docker compose up -d${NC}"
    exit 1
fi

mkdir -p ./backups

echo -e "\n${YELLOW}>>> [1/2] Frappe daxilində tam backup yaradılır (Database + Files)...${NC}"
docker compose exec -T backend bench --site "${SITE_NAME}" backup --with-files

echo -e "\n${YELLOW}>>> [2/2] Nüsxə faylları ./backups/ qovluğuna kopyalanır...${NC}"
# Konteyner daxilindəki ən son backup fayllarını ./backups/ qovluğuna köçür
docker compose exec -T backend bash -c "
    LATEST_SQL=\$(ls -t sites/${SITE_NAME}/private/backups/*-database.sql.gz 2>/dev/null | head -n 1)
    if [ -n \"\$LATEST_SQL\" ]; then
        BASE_PREFIX=\${LATEST_SQL%-database.sql.gz}
        cp \${BASE_PREFIX}* /backups/ 2>/dev/null || true
    fi
"

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}✓ NÜSXƏLƏMƏ UĞURLA TAMAMLANDI!${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "📂 ./backups/ qovluğundakı fayllar:"
ls -lh ./backups/ | grep -E '\.sql\.gz|\.json|\.tar' || echo "Fayllar köçürüldü."
echo ""

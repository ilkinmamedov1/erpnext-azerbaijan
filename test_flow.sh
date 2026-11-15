#!/usr/bin/env bash
# =================================================================
# ERPNext Azərbaycan - 1-Komanda ilə Test və Yoxlanış Skripti
# =================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "================================================================="
echo "   🇦🇿  ERPNEXT AZƏRBAYCAN ƏMƏLİYYAT VƏ AUDİT YOXLANIŞI  🇦🇿   "
echo "================================================================="
echo -e "${NC}"

echo -e "${YELLOW}>>> Konteyner daxilində tam kommersiya dövriyyəsi icra edilir...${NC}\n"

docker compose exec -T -w /home/frappe/frappe-bench/sites backend /home/frappe/frappe-bench/env/bin/python /scripts/run_tests.py

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}✅ BÜTÜN ƏMƏLİYYATLAR VƏ BAŞ KİTAB BALANSI 100% TƏSDİQLƏNDİ!${NC}"
echo -e "${GREEN}=================================================================${NC}\n"

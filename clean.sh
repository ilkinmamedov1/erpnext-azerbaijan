#!/usr/bin/env bash
# =================================================================
# ERPNext Azərbaycan - Test Məlumatlarını Təmizləmə Skripti
# =================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "================================================================="
echo "   🧹 ERPNEXT AZƏRBAYCAN - TEST MƏLUMATLARININ TƏMİZLƏNMƏSİ   "
echo "================================================================="
echo -e "${NC}"

echo -e "${YELLOW}>>> Test sənədləri (fakturalar, sifarişlər, test məhsulları) təmizlənir...${NC}\n"

docker compose exec -T -w /home/frappe/frappe-bench/sites backend /home/frappe/frappe-bench/env/bin/python /scripts/clean_test_data.py

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}✨ SAYT TAM TƏMİZDİR! İstehsalat (Real) istifadəyə tam hazırdır.${NC}"
echo -e "${GREEN}=================================================================${NC}\n"

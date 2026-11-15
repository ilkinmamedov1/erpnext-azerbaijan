#!/usr/bin/env bash
# =================================================================
# ERPNext Azərbaycan - 1-Komanda ilə Quraşdırılma Skripti
# Müəllif: İlkin Məmmədov (https://github.com/ilkinmamedov1)
# =================================================================

set -e

# Avtomatik klonlama yoxlanışı (curl ilə icra edildikdə)
if [ ! -f "compose.yaml" ]; then
    echo ">>> Layihə faylları aşkar edilmədi. GitHub-dan yüklənir..."
    TARGET_DIR="${HOME}/erpnext-azerbaijan"
    if [ ! -d "$TARGET_DIR" ]; then
        git clone https://github.com/ilkinmamedov1/erpnext-azerbaijan.git "$TARGET_DIR"
    fi
    cd "$TARGET_DIR"
fi

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "================================================================="
echo "   🇦🇿  ERPNEXT AZƏRBAYCAN LOKALİZASİYASI & HESABLAR PLANI  🇦🇿   "
echo "================================================================="
echo -e "${NC}"

# 1. Preflight yoxlamaları
echo -e "${YELLOW}>>> [1/5] Tələblər və konfiqurasiya yoxlanılır...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}XƏTA: Docker quraşdırılmayıb. Zəhmət olmasa Docker quraşdırın.${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}XƏTA: Docker Compose v2 quraşdırılmayıb.${NC}"
    exit 1
fi

# .env faylını təmin et
if [ ! -f .env ]; then
    echo -e "${YELLOW}   .env faylı tapılmadı. .env.example əsasında yaradılır...${NC}"
    cp .env.example .env
fi

# Qovluqları təmin et
mkdir -p backups nginx/ssl

# Mövcud dəyişənləri oxu
export $(grep -v '^#' .env | xargs -d '\n' 2>/dev/null || true)

# Şirkət parametrlərinin interaktiv soruşulması (əgər terminal interaktivdirsə)
if [ -t 0 ]; then
    echo -e "\n${CYAN}--- Şirkət və Sistem Parametrlərini Təyin Edin (Dəyişməmək üçün [Enter] basın) ---${NC}"
    
    read -p "🏢 Şirkətin adı [cari: ${COMPANY_NAME:-TEST MMC}]: " INPUT_COMP
    COMPANY_NAME=${INPUT_COMP:-${COMPANY_NAME:-TEST MMC}}

    read -p "🏷️  Şirkət abreviaturası [cari: ${COMPANY_ABBR:-TM}]: " INPUT_ABBR
    COMPANY_ABBR=${INPUT_ABBR:-${COMPANY_ABBR:-TM}}

    read -p "🔢 VÖEN nömrəsi [cari: ${COMPANY_TAX_ID:-1300000001}]: " INPUT_TAX
    COMPANY_TAX_ID=${INPUT_TAX:-${COMPANY_TAX_ID:-1300000001}}

    read -p "🌐 Veb Port [cari: ${HTTP_PORT:-8080}]: " INPUT_PORT
    HTTP_PORT=${INPUT_PORT:-${HTTP_PORT:-8080}}

    read -p "🔑 Administrator şifrəsi [cari: ${ADMIN_PASSWORD:-admin}]: " INPUT_PW
    ADMIN_PASSWORD=${INPUT_PW:-${ADMIN_PASSWORD:-admin}}

    read -p "🔐 Verilənlər bazası (MariaDB root) şifrəsi [cari: ${DB_ROOT_PASSWORD:-admin}]: " INPUT_DB_PW
    DB_ROOT_PASSWORD=${INPUT_DB_PW:-${DB_ROOT_PASSWORD:-admin}}

    read -p "⚙️  Gunicorn Worker sayı [cari: ${WORKERS:-2}]: " INPUT_WORKERS
    WORKERS=${INPUT_WORKERS:-${WORKERS:-2}}

    # .env faylını yenilə
    cat << EOF > .env
# ==============================================================================
# 🇦🇿 ERPNext Azərbaycan - Konfiqurasiya Parametrləri (.env)
# ==============================================================================
SITE_NAME=${SITE_NAME:-frontend}
HTTP_PORT=${HTTP_PORT}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

COMPANY_NAME=${COMPANY_NAME}
COMPANY_ABBR=${COMPANY_ABBR}
COMPANY_TAX_ID=${COMPANY_TAX_ID}
COMPANY_DOMAIN=${COMPANY_DOMAIN:-Distribution}

WORKERS=${WORKERS}

DEFAULT_CURRENCY=AZN
TIMEZONE=Asia/Baku
COUNTRY=Azerbaijan
EOF
fi

HTTP_PORT=${HTTP_PORT:-8080}
SITE_NAME=${SITE_NAME:-frontend}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
COMPANY_NAME=${COMPANY_NAME:-TEST MMC}

echo -e "\n${GREEN}   ✓ Konfiqurasiya təsdiqləndi:${NC}"
echo -e "${GREEN}   ✓ Şirkət: ${COMPANY_NAME} (${COMPANY_ABBR:-TM}) | VÖEN: ${COMPANY_TAX_ID:-1300000001}${NC}"
echo -e "${GREEN}   ✓ Port: ${HTTP_PORT} | Sayt: ${SITE_NAME}${NC}"

# 2. Port yoxlanışı
if ss -tuln 2>/dev/null | grep -q ":${HTTP_PORT} "; then
    echo -e "${YELLOW}   XƏBƏRDARLIQ: ${HTTP_PORT} portu sistemdə aktivdir.${NC}"
fi

# 3. Docker konteynerlərini işə sal
echo -e "\n${YELLOW}>>> [2/5] Docker servisləri işə salınır...${NC}"
docker compose up -d db redis-cache redis-queue configurator backend frontend websocket queue-short queue-long scheduler create-site

# 4. Saytın və Azərbaycan lokalizasiyasının tamamlanmasını izlə
echo -e "\n${YELLOW}>>> [3/5] Sayt qurulur, AZN valyutası və 427 Hesablar Planı tətbiq edilir...${NC}"
echo -e "   (Zəhmət olmasa gözləyin, proses bir qədər vaxt apara bilər...)\n"

docker compose logs -f create-site

# 5. Veb interfeysin hazırlığını yoxla
echo -e "\n${YELLOW}>>> [4/5] Veb interfeys yoxlanılır (http://localhost:${HTTP_PORT})...${NC}"
MAX_RETRIES=40
COUNT=0
READY=false

while [ $COUNT -lt $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${HTTP_PORT}" || true)
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
        READY=true
        break
    fi
    sleep 3
    COUNT=$((COUNT + 1))
    echo -n "."
done
echo ""

if [ "$READY" = true ]; then
    echo -e "\n${GREEN}=================================================================${NC}"
    echo -e "${GREEN}🎉 TƏBRİKLƏR! ERPNEXT AZƏRBAYCAN UĞURLA QURAŞDIRILDI VƏ HAZIRDIR!${NC}"
    echo -e "${GREEN}=================================================================${NC}"
    echo -e "🔗 Veb Ünvan:        ${CYAN}http://localhost:${HTTP_PORT}${NC}"
    echo -e "👤 İstifadəçi adı:   ${CYAN}Administrator${NC}"
    echo -e "🔑 Şifrə:            ${CYAN}${ADMIN_PASSWORD}${NC}"
    echo -e "🏢 Şirkət:           ${CYAN}${COMPANY_NAME}${NC}"
    echo -e "💰 Valyuta:          ${CYAN}AZN (₼)${NC}"
    echo -e "📑 Hesablar Planı:   ${CYAN}427 Standart Azərbaycan Hesabı (Maliyyə Nazirliyi standartı)${NC}"
    echo -e "🧾 Hesab-Faktura:    ${CYAN}Azərbaycan standartında Qaimə çap formatı aktivdir${NC}"
    echo -e "✨ İlkin Vəziyyət:    ${CYAN}100% Təmiz (heç bir saxta/test fakturası yoxdur)${NC}"
    echo -e "\n${YELLOW}>>> [5/5] Əməliyyat dövriyyəsini test etmək istədikdə bu komandanı icra edin:${NC}"
    echo -e "   ${CYAN}./test_flow.sh${NC}\n"
else
    echo -e "${RED}XƏBƏRDARLIQ: Sayt hələ tam HTTP cavabı vermir. 'docker compose logs frontend' ilə baxa bilərsiniz.${NC}"
fi

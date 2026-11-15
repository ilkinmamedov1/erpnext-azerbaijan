# 🇦🇿 ERPNext Azərbaycan Lokalizasiyası & Standart Hesablar Planı (v15)

Azərbaycan Respublikasının qanunvericiliyinə, Vergi Məcəlləsinə və Maliyyə Nazirliyinin Milli Mühasibat Standartlarına tam uyğunlaşdırılmış **427 Hesabdan ibarət Hesablar Planı**, **AZN valyutası**, **ƏDV (18%)**, **Bank və Kassa**, **Azərbaycan dilində Nömrələmə Seriyaları** və **Rəsmi Hesab-Faktura çap forması** ilə təchiz olunmuş, 1 komanda ilə qurulan ERPNext v15 Docker paketi.

---

## 📌 Layihə Haqqında

**ERPNext** — qlobal miqyasda minlərlə müəssisə tərəfindən istifadə olunan, dünyanın ən güclü və etibarlı açıq qaynaqlı ERP (Müəssisə Resurslarının İdarə Edilməsi) sistemidir. 

Lakin rəsmi ERPNext distributivində Azərbaycan dili, AZN valyutası və yerli mühasibat uçotu standartları olmadığından, şirkətlər hər dəfə sıfırdan aylar boyu fərdi sazlama aparmağa məcbur qalırdılar. 

Bu layihə həmin problemi kökündən həll edir:
- 🚀 **1-Komanda ilə Quraşdırılma:** Docker vasitəsilə 2 dəqiqə ərzində bütün sistem işə düşür.
- 🏢 **Öz Şirkət Adınızı Təyin Etmə:** Quraşdırma zamanı terminalda şirkətinizin adını, abreviaturasını, VÖEN və bank rekvizitlərini birbaşa daxil edə bilərsiniz.
- ✨ **100% Təmiz Baza (Zero Dummy Data):** Sistemdə heç bir saxta və ya köhnə test sənədi/fakturası yoxdur. Quraşdırıldıqdan dərhal sonra təmiz şəkildə real biznes əməliyyatlarınızı daxil etməyə hazırdır.
- 📑 **Maliyyə Nazirliyinin 427 Hesabı:** Bütün sintetik və analitik hesablar iyerarxik ağac formasında avtomatik qurulur.

---

## ⚡ 1-Komanda ilə Quraşdırılma (Quickstart)

### Tələblər:
- Əməliyyat sistemi: Linux (Ubuntu, Debian, CentOS), macOS və ya Windows (WSL2)
- [Docker](https://docs.docker.com/get-docker/) və [Docker Compose v2](https://docs.docker.com/compose/)

### 🚀 1-Sətirlik Birbaşa Quraşdırma (Ən Asan Yol):

Terminalda birbaşa bu komandanı icra edin:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ilkinmamedov1/erpnext-azerbaijan/main/install.sh)"
```

Və ya klassik üsulla:
```bash
git clone https://github.com/ilkinmamedov1/erpnext-azerbaijan.git
cd erpnext-azerbaijan
./install.sh
```

Skript işə düşdükdə sizdən şirkətinizin məlumatlarını daxil etməyi xahiş edəcək (standart dəyərləri saxlamaq üçün sadəcə `Enter` basa bilərsiniz):
```text
🏢 Şirkətin adı [cari: TEST MMC]: Şirkətim MMC
🏷️  Şirkət abreviaturası [cari: TM]: ŞM
🔢 VÖEN nömrəsi [cari: 1300000001]: 1400123451
🌐 Veb Port [cari: 8080]: 8080
🔑 Administrator şifrəsi [cari: admin]: GüclüAdminŞifrəsi
🔐 Verilənlər bazası (MariaDB root) şifrəsi [cari: admin]: GüclüBazaŞifrəsi
🏦 Bank adı [cari: Bank Hesabı]: Bank Hesabı (və ya istədiyiniz bank)
💳 Bank İBAN (istəyə görə) [cari: ]: AZ00XXXX00000000000000000000
🌐 Bank SWIFT (istəyə görə) [cari: ]: 
```

Quraşdırma tamamlandıqdan sonra:
- 🌐 **Veb Ünvan:** [http://localhost:8080](http://localhost:8080)
- 👤 **İstifadəçi adı:** `Administrator`
- 🔑 **Şifrə:** Təyin etdiyiniz şifrə (və ya `admin`)

---

## 📖 Modullar Üzrə Ətraflı İstifadə Təlimatı

Sistem Azərbaycan biznes mühitinə uyğunlaşdırılmış aşağıdakı əsas modulları təqdim edir:

### 1. 🏛️ Mühasibatlıq və Maliyyə (Accounting)

#### A. Hesablar Planı (Chart of Accounts)
Sistem Maliyyə Nazirliyinin təsdiq etdiyi 8 əsas bölmə üzrə 427 hesabı dərhal istifadəyə təqdim edir:
- **1 - Uzunmüddətli Aktivlər:** Torpaq, tikili və avadanlıqlar (111), TTA üzrə yığılmış amortizasiya (112), Qeyri-maddi aktivlər (101).
- **2 - Qısamüddətli Aktivlər:** Material ehtiyatları (201), Mallar (205), Hazır məhsul (204), Alıcıların debitor borcları (211), Kassa (221), Bank hesabları (223), ƏDV əvəzləşməsi (241).
- **3 - Kapital:** Nizamnamə kapitalı (301), Bölüşdürülməmiş mənfəət (341), Ehtiyat kapitalı (321).
- **4 - Uzunmüddətli Öhdəliklər:** Uzunmüddətli bank kreditləri (401), Faiz borcları (402).
- **5 - Qısamüddətli Öhdəliklər:** Təchizatçılara kreditor borcları (531), Vergi öhdəlikləri / ƏDV (521), Əməkhaqqı borcları (533).
- **6 - Gəlirlər:** Əsas əməliyyat gəlirləri / Satış (601), Sair əməliyyat gəlirləri (611), Valyuta məzənnə fərqi mənfəəti (631).
- **7 - Xərclər:** Satılmış malların dəyəri / Maya dəyəri - SDX (701), Kommersiya xərcləri (711), İnzibati xərclər (721).
- **8 - Maliyyə Nəticələri:** Hesabat dövrünün xalis mənfəəti / zərəri (801).

#### B. ƏDV və Vergi Mexanizmi
- **ƏDV 18%:** Satış fakturasında avtomatik `521.01 - ƏDV öhdəliyi` hesabına kredit yazılır.
- **ƏDV Əvəzləşdirilən (18%):** Alış fakturasında avtomatik `241.01 - ƏDV əvəzləşməsi (yerli)` hesabına debet yazılır.
- **ƏDV 0% (İxrac)** və **ƏDV-dən Azad** şablonları da hazırdır.

#### C. Valyuta və Mərkəzi Bank (AMB) Məzənnələri
Sistem AZN (₼) valyutası üzərində qurulub. USD, EUR, RUB, TRY və GBP məzənnələri avtomatik tanınır. Xarici valyutada faktura yazıldıqda məzənnə fərqi avtomatik `631.04` (gəlir) və ya `731` (zərər) hesabına silinir.

#### D. Maliyyə Hesabatları
Birbaşa menyudan real vaxt rejimində hesabatlar formalaşır:
- **Balans Hesabatı (Balance Sheet)**
- **Mənfəət və Zərər Hesabatı (Profit and Loss)**
- **Baş Kitab (General Ledger)**
- **Dövriyyə Cədvəli (Trial Balance)**
- **Debitor və Kreditor Yaşlanma Hesabatı (Accounts Receivable / Payable Aging)**

---

### 2. 💼 Satış və Müştərilər (Selling)

- **Müştərilər (Customer):** Hər bir müştərinin kartoçkasında **VÖEN** sahəsi mövcuddur. Müştəri tipi: Şirkət (Hüquqi şəxs) və ya Fərdi sahibkar.
- **Satış Sifarişi (`SS-.YYYY.-.#####`):** Müştəri ilə razılaşdırılmış qiymət və miqdar üzrə sifariş sənədi.
- **Təhvil Qaiməsi (`TQ-.YYYY.-.#####`):** Malların anbardan çıxarılaraq müştəriyə təhvil verilməsi.
- **Satış Fakturası / Qaiməsi (`SQ-.YYYY.-.#####`):** Satışın rəsmiləşdirilməsi və ƏDV-nin hesablanması.
- **Rəsmi "Hesab-Faktura (Azərbaycan)" Çapı:** 
  Satış qaiməsində `Çap et` düyməsini basdıqda Azərbaycan standartlarına uyğun format açılır:
  - Şirkətinizin və Müştərinin VÖEN-i
  - Bank və İBAN rekvizitləri (İstədiyiniz bank hesabı və İBAN)
  - Xalis məbləğ, 18% ƏDV və Yekun məbləğ
  - Məbləğin Azərbaycan dilində sözlə yazılışı
  - Direktor, Baş Mühasib imzaları və **M.Y. (Möhür yeri)**

---

### 3. 🛒 Satınalma və Təchizat (Buying)

- **Təchizatçılar (Supplier):** Yerli və xarici distribüterlərin VÖEN və bank rekvizitləri ilə qeydiyyatı.
- **Alış Sifarişi (`AS-.YYYY.-.#####`):** Təchizatçıya göndərilən sifariş qaiməsi.
- **Mədaxil Qaiməsi (`MQ-.YYYY.-.#####`):** Malların anbara fiziki qəbulu.
- **Alış Qaiməsi (`AQ-.YYYY.-.#####`):** Fakturanın qeydiyyatı. 18% ƏDV avtomatik olaraq `241.01 - ƏDV əvəzləşməsi` hesabına düşür.

---

### 4. 📦 Anbar və Material Ehtiyatları (Stock)

#### A. Çoxanbarlı Struktur:
- **Bütün Anbarlar** (Ana Qrup)
  - ├── **Əsas Anbar (Mallar)** ➔ `205.01` hesabı
  - ├── **Hazır Məhsul Anbarı** ➔ `204.01` hesabı
  - ├── **Xammal və Materiallar Anbarı** ➔ `201.01.01` hesabı
  - ├── **Bitməmiş İstehsalat Anbarı** ➔ `202.01` hesabı
  - └── **Tranzit Anbar (Yolda olan mallar)** ➔ `207` hesabı

#### B. Nomenklatura və Ölçü Vahidləri:
- Məhsul kartoçkası (Item Code, Barkod, Brend).
- Standart Azərbaycan ölçü vahidləri: **Ədəd**, **Qutu**, **Dəst**, **Paçka**, **Rulon**, **Qram**, **Kq**, **Ton**.
- Daxili Yerdəyişmə (Material Transfer): Məsələn, Əsas Anbardan Hazır Məhsul Anbarına daxili köçürmə.
- İnventarizasiya və Sayım (Stock Reconciliation): Faktiki anbar sayımı ilə sistem qalıqlarının uyğunlaşdırılması.

---

### 5. 💳 Kassa və Bank Əməliyyatları (Payments)

- **Ödəniş Sənədləri (`ÖD-.YYYY.-.#####`):**
  - **Nağd Kassa (221.01):** Kassa məxaric (xərclərin nağd ödənilməsi) və mədaxil əməliyyatları.
  - **Bank Köçürməsi (223.01):** Təchizatçılara köçürmələr və müştərilərdən daxilolmalar.
  - **POS-Terminal / Kart:** Pərakəndə satış nöqtələrindən daxilolmalar.
  - **ƏDV Depozit Hesabı (226):** Vergi orqanının ƏDV depozit sub-uçot hesabı vasitəsilə ƏDV-nin birbaşa ödənilməsi və əvəzləşdirilməsi.

---

## ⚙️ Peşəkar Konfiqurasiya (.env Faylı)

Sistem bütün parametrlərini `.env` faylından oxuyur. Layihədə hazır `.env.example` nümunəsi mövcuddur.

### Əsas Konfiqurasiya Sahələri:
| Parametr | Standart Dəyər | Təsvir |
|---|---|---|
| `SITE_NAME` | `frontend` | ERPNext sayt adı |
| `HTTP_PORT` | `8080` | Veb interfeysin açılacağı port (istəsəniz `80` və ya `8080` edin) |
| `ADMIN_PASSWORD` | `admin` | ERPNext `Administrator` istifadəçisinin giriş şifrəsi |
| `DB_ROOT_PASSWORD` | `admin` | **MariaDB 10.6 root verilənlər bazası şifrəsi** (istədiyiniz güclü şifrə) |
| `DB_HOST` | `db` | MariaDB konteynerinin daxili host adı |
| `DB_PORT` | `3306` | MariaDB portu |
| `COMPANY_NAME` | `TEST MMC` | Şirkətinizin rəsmi adı (hesabatlarda və qaimələrdə çıxır) |
| `COMPANY_ABBR` | `TM` | Şirkət abreviaturası (hesab kodlarının sonluğunda istifadə olunur) |
| `COMPANY_TAX_ID` | `1300000001` | Şirkətin 10 rəqəmli rəsmi VÖEN nömrəsi |
| `BANK_NAME` | `Bank Hesabı` | Şirkətinizin bank adı (qaimələrdə və köçürmələrdə çıxır) |
| `BANK_IBAN` | *(boş)* | Bankın 28 simvollu İBAN hesabı (istəyə görə) |
| `BANK_SWIFT` | *(boş)* | Bankın beynəlxalq SWIFT kodu (istəyə görə) |

### 💡 Avtomatik Fallback (Boş Sahələrin Qorunması):
- Əgər `.env` faylında hər hansı parametr boş buraxılarsa və ya qeyd olunmazsa, **1-komanda ilə quraşdırma skripti dayanmır**!
- Skript avtomatik olaraq təmiz, sazlanmış və işlək standart dəyərləri (`admin`, `8080`, `Bank Hesabı` və s.) tətbiq edir.
- İstənilən vaxt `.env` faylını açıb parametrləri redaktə edə bilərsiniz.

---

## 🛠️ Əlavə Köməkçi Skriptlər

| Skript | Təsvir |
|---|---|
| `./install.sh` | Sistemi 1 komanda ilə interaktiv quraşdırır. |
| `./test_flow.sh` | Bütün alış, satış, anbar və kassa dövriyyəsini avtomatik icra edib Baş Kitab (GL) balansını yoxlayır. |
| `./clean.sh` | Test dövriyyəsindən sonra yaranan test fakturalarını və məhsullarını təmizləyib bazanı sıfır vəziyyətinə qaytarır. |

### Sistemi İdarə Etmək:
```bash
# Arxa planda işə salmaq:
docker compose up -d

# Sistemi müvəqqəti dayandırmaq:
docker compose stop

# Konteynerləri dayandırmaq (məlumatlar bazada qalır):
docker compose down

# Loqlara canlı baxmaq:
docker compose logs -f backend
```

### 🗑️ Sistemi Kompüterdən Tamamilə Silmək:
Əgər ERPNext sistemini və bütün verilənlər bazasını kompüterdən tamamilə təmizləmək istəsəniz:
```bash
docker compose down -v
```
*(Bu əmr bütün konteynerləri, şəbəkəni və daxili MariaDB həcmlərini kompüterdən tamamilə silir).*

---

## 📁 Qovluq Strukturu

```
erpnext-azerbaijan/
├── compose.yaml              # Docker Compose servisləri (MariaDB, Redis, Backend, Frontend)
├── .env.example              # Konfiqurasiya şablonu
├── install.sh                # İnteraktiv 1-klik quraşdırıcı
├── test_flow.sh              # Tam audit və əməliyyat testi
├── clean.sh                  # Test məlumatlarını təmizləyici
├── README.md                 # Təlimat sənədi
├── .gitignore
├── data/
│   └── azerbaijan_coa.csv    # 427 Rəsmi Azərbaycan Hesablar Planı (CSV formatında)
└── scripts/
    ├── init_azerbaijan.py    # Master lokalizasiya və avtomatlaşdırma skripti
    ├── run_tests.py          # Bütün dövriyyələri simulyasiya edən test skripti
    ├── clean_test_data.py    # Baza təmizləmə skripti
    └── legacy/               # Ehtiyat/tarixi skriptlər
```

---

## 👨‍💻 Müəllif & Əlaqə
- **Müəllif:** İlkin Məmmədov ([@ilkinmamedov1](https://github.com/ilkinmamedov1))
- **Lisenziya:** MIT License — İstənilən şəxs və ya şirkət tərəfindən sərbəst istifadə oluna, dəyişdirilə və yayıla bilər.

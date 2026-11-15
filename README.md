# 🇦🇿 ERPNext Azərbaycan Lokalizasiyası & Hesablar Planı (v15)

Azərbaycan Respublikası Maliyyə Nazirliyinin standartlarına uyğunlaşdırılmış **427 Hesabdan ibarət Milli Mühasibat Hesablar Planı**, **AZN valyutası**, **ƏDV (18%)**, **Bank və Kassa**, **Azərbaycan dilində Nömrələmə Seriyaları** və **Hesab-Faktura (Qaimə) çap forması** ilə təchiz olunmuş tam avtomatlaşdırılmış 1-komandalı ERPNext v15 Docker paketi.

---

## ⚡ 1-Komanda ilə Quraşdırılma (Quickstart)

Heç bir əlavə sazlama tələb olunmur. Sadəcə repozitoriyanı klonlayın və quraşdırma skriptini başladın:

```bash
git clone https://github.com/ilkinmamedov1/erpnext-azerbaijan.git
cd erpnext-azerbaijan
./install.sh
```

Quraşdırma başa çatdıqdan sonra:
- 🌐 **Veb Ünvan:** [http://localhost:8080](http://localhost:8080)
- 👤 **İstifadəçi adı:** `Administrator`
- 🔑 **Şifrə:** `admin` *(və ya `.env` faylında təyin etdiyiniz şifrə)*

---

## 🧪 Əməliyyatların və Baş Kitabın Yoxlanılması (Verification)

Sistemin tam işlək olduğunu və mühasibat balansının 100% oturduğunu yoxlamaq üçün test skriptini işə salın:

```bash
./test_flow.sh
```

Bu skript avtomatik olaraq:
1. **Məhsul, Müştəri və Təchizatçı** yaradır (VÖEN nömrələri ilə).
2. **Alış Dövriyyəsi:** Alış Sifarişi (AS) ➔ Mədaxil Qaiməsi (MQ) ➔ Alış Fakturası (AQ, 18% ƏDV ilə) ➔ Bank Köçürməsi (ÖD).
3. **Satış Dövriyyəsi:** Satış Sifarişi (SS) ➔ Təhvil Qaiməsi (TQ) ➔ Satış Fakturası (SQ, 18% ƏDV ilə) ➔ Bank Mədaxili (ÖD).
4. **Anbar Dövriyyəsi:** Əsas Anbardan Hazır Məhsul Anbarına daxili yerdəyişmə.
5. **Kassa Xərci:** Kassadan (221.01) inzibati xərclərin (721.19) ödənilməsi.
6. **Mühasibat Auditi:** Baş Kitab (General Ledger) debet/kredit fərqini (0.00 ₼) və Anbar qalıqlarını yoxlayır.

---

## 📦 Paketə Daxil Olan Xüsusiyyətlər

### 1. 📑 427 Hesabdan İbarət Standart Azərbaycan Hesablar Planı
- **Bölmə 1:** Uzunmüddətli Aktivlər (Əsas vəsaitlər, Qeyri-maddi aktivlər, Amortizasiya)
- **Bölmə 2:** Qısamüddətli Aktivlər (Materiallar, Mallar, Debitor borclar, Kassa, Bank)
- **Bölmə 3:** Kapital (Nizamnamə kapitalı, Bölüşdürülməmiş mənfəət, Ehtiyatlar)
- **Bölmə 4:** Uzunmüddətli Öhdəliklər (Uzunmüddətli kreditlər və borclar)
- **Bölmə 5:** Qısamüddətli Öhdəliklər (Kreditor borclar, ƏDV öhdəliyi, Əməkhaqqı borcları)
- **Bölmə 6:** Gəlirlər (Əsas əməliyyat gəlirləri, Mal satışı, Xidmət göstərilməsi)
- **Bölmə 7:** Xərclər (Satışın maya dəyəri - SDX, İnzibati xərclər, Kommersiya xərcləri)
- **Bölmə 8:** Maliyyə Nəticələri (Hesabat dövrünün mənfəəti/zərəri)

### 2. 🏛️ Şirkət İlkin Mühasibat Hesablarının Avtomatik Əlaqələndirilməsi
- **Kassa:** `221.01 - Kassa - AZN`
- **Bank:** `223.01 - Bank hesabı - AZN (Əsas bank)`
- **Alıcılar:** `211.01.01 - Yerli alıcılar - hüquqi şəxslər`
- **Malsatanlar:** `531.01.01 - Yerli malsatanlar - hüquqi şəxslər`
- **Mallar:** `205.01 - Mallar - anbar`
- **Gəlir:** `601.02.01 - Mal satışı - pərakəndə`
- **Xərc (SDX):** `701.04 - Alınan malların dəyəri (SDX)`
- **ƏDV Öhdəliyi:** `521.01 - ƏDV öhdəliyi`
- **ƏDV Əvəzləşməsi:** `241.01 - ƏDV əvəzləşməsi - yerli alışlar` və `241.02 - idxal`
- **ƏDV Depoziti:** `226 - ƏDV sub-uçot hesabı`

### 3. 🏢 Azərbaycan Nomenklaturasına Uyğun Anbar Strukturu
- **Bütün Anbarlar** (Ana qrup)
- **Əsas Anbar (Mallar)** ➔ `205.01`
- **Hazır Məhsul Anbarı** ➔ `204`
- **Xammal və Materiallar Anbarı** ➔ `201`
- **Bitməmiş İstehsalat Anbarı** ➔ `202`
- **Tranzit Anbar (Yolda olan mallar)** ➔ `207`

### 4. 🏷️ Sənəd Nömrələmə Seriyaları (Naming Series)
- Satış Qaiməsi: `SQ-.YYYY.-.#####`
- Alış Qaiməsi: `AQ-.YYYY.-.#####`
- Satış Sifarişi: `SS-.YYYY.-.#####`
- Alış Sifarişi: `AS-.YYYY.-.#####`
- Təhvil Qaiməsi: `TQ-.YYYY.-.#####`
- Mədaxil Qaiməsi: `MQ-.YYYY.-.#####`
- Ödəniş Qəbzi: `ÖD-.YYYY.-.#####`
- Memorial Qaimə (Journal Entry): `MƏ-.YYYY.-.#####`

### 5. 🧾 Rəsmi "Hesab-Faktura (Azərbaycan)" Çap Formatı
- Şirkət və Müştəri VÖEN rekvizitləri
- Bank və İBAN rekvizitləri (Kapital Bank ASC və s.)
- Əsas məbləğ, 18% ƏDV ayrılması və yekun ödəniləcək məbləğ
- Məbləğin sözlə avtomatik yazılışı
- Rəhbər, Baş Mühasib və M.Y. (Möhür yeri) sahələri

### 6. 💱 Mərkəzi Bank (AMB) Məzənnə Şablonları
- USD/AZN (1.7000), EUR/AZN (1.8450), RUB/AZN, TRY/AZN, GBP/AZN

---

## ⚙️ Konfiqurasiya (.env)

Quraşdırmadan öncə `.env` faylını redaktə edərək öz şirkətinizin məlumatlarını təyin edə bilərsiniz:

```ini
SITE_NAME=frontend
HTTP_PORT=8080
ADMIN_PASSWORD=admin
DB_ROOT_PASSWORD=admin

COMPANY_NAME=TEST MMC
COMPANY_ABBR=TM
COMPANY_TAX_ID=1300000001

BANK_NAME=Kapital Bank ASC
BANK_SWIFT=AIIBAZ2X
BANK_IBAN=AZ43AIIB38010019440026214101
```

---

## 🛠️ Qovluq Strukturu

```
erpnext-azerbaijan/
├── compose.yaml              # Docker Compose konfiqurasiyası
├── .env.example              # Mühit parametrləri şablonu
├── install.sh                # 1-komanda ilə quraşdırıcı
├── test_flow.sh              # 1-komanda ilə əməliyyat testi
├── README.md                 # Təlimat sənədi
├── .gitignore
├── data/
│   └── azerbaijan_coa.csv    # 427 Standart Hesabın tam siyahısı
└── scripts/
    ├── init_azerbaijan.py    # Master lokalizasiya və avtomatlaşdırma skripti
    └── run_tests.py          # Tam dövriyyə və audit yoxlanışı
```

---

## 📜 Lisenziya & Müəllif
Müəllif: **İlkin Məmmədov** ([@ilkinmamedov1](https://github.com/ilkinmamedov1))  
Lisenziya: MIT License.

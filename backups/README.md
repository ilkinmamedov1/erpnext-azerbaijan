# 💾 ERPNext Tam Nüsxələmə və Bərpa (Backup & Restore)

Bu qovluq ERPNext sisteminin tam verilənlər bazası (SQL), sayt konfiqurasiyası (JSON) və fayl arxivlərini (TAR) saxlamaq üçün nəzərdə tutulub.

---

## 📁 Frappe/ERPNext Backup Fayllarının Strukturu:

Frappe tam nüsxələmə zamanı 4 əsas fayl yaradır:
1. `*-database.sql.gz` — Bütün MariaDB cədvəllərinin və qeydlərinin sıxılmış SQL nüsxəsi.
2. `*-site_config_backup.json` — Saytın şifrələri, açarları və xüsusi sazlamaları.
3. `*-files.tar` — Sistemə yüklənmiş açıq fayllar (şəkillər, logolar, açıq sənədlər).
4. `*-private-files.tar` — Gizli fayllar və rəsmi elektron əlavələr.

---

## 🚀 1. Mövcud Backup-ı Bərpa Etmək (Restore):
Əgər əlinizdə köhnə ERPNext saytınızdan götürülmüş backup faylları varsa:
1. `.sql.gz`, `.json` və `.tar` fayllarınızı birbaşa bu `backups/` qovluğuna kopyalayın.
2. Layihənin əsas qovluğunda bu komandanı icra edin:
   ```bash
   ./restore.sh
   ```
3. Skript avtomatik olaraq faylları aşkar edəcək və bazaya tam bərpa edəcək!

---

## 📦 2. Cari Saytın Tam Backup-ını Götürmək (Backup):
İstənilən vaxt işləyən saytınızın nüsxəsini götürmək üçün:
```bash
./backup.sh
```
Skript arxa planda bazanı və faylları arxivləyib birbaşa bu `backups/` qovluğuna çıxaracaq.

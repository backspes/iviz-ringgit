# iviz Ringgit — Malaysian Personal Finance & Credit Card Affiliate Portal (SSG)

Portal perbandingan kewangan bebas Malaysia berasaskan Static Site Generator (Python SSG) berprestasi tinggi yang dihoskan di Cloudflare Pages.

- **Domain Utama**: `https://ringgit.iviztrading.com`
- **Senibina**: Hub-and-Spoke 3-Tier Enterprise Silo
- **Pematuhan**: Standard Enterprise (Zero Hardcoded Secrets, Zero 404 Policy, AEO/GEO Optimized)

---

## 1. Senibina Navigasi & Pipeline Halaman (Hub-and-Spoke)

```
[ Tier 1: Laman Utama / Homepage ]
  ↳ index.html (Gambaran menyeluruh, trust signals, kad pilihan)
       │
       ├── [ Tier 2: Master Hubs ]
       │     ├── kad-kredit.html (34 Kad Kredit — Master Category Hub)
       │     ├── pinjaman-peribadi.html (10 Pinjaman Bank — Master Loans Hub)
       │     └── skor-kredit.html (Semakan Skor Kredit Rasmi Experian/CCRIS)
       │
       ├── [ Tier 3: Sub-Category Listicle Hubs ]
       │     ├── Kad: /kad-kredit-petrol.html, /kad-kredit-shopping.html, /kad-kredit-cashback.html,
       │     │        /kad-kredit-islamic.html, /kad-kredit-travel.html, /kad-kredit-gaji-rendah.html
       │     └── Pinjaman: /pinjaman-gaji-rendah.html, /pinjaman-islamic.html,
       │                   /pinjaman-kelulusan-pantas.html, /pinjaman-penjawat-awam.html
       │
       └── [ Tier 4: Product Detail Pages (Spokes) ]
             ├── 34 Ulasan Kad Kredit (/maybank-shopee-visa-platinum.html, /rhb-shell-visa-credit-card.html, ...)
             └── 10 Ulasan Pinjaman (/alliance-cashfirst.html, /rhb-personal-financing.html, ...)
```

---

## 2. Kitaran Hayat Produk & Promosi (Lifecycle Management & Zero 404 Policy)

Mengikut amalan standard enterprise:
1. **Zero 404 Policy**: Halaman produk yang telah luput atau dipausekan oleh pihak bank **TIDAK AKAN DIPADAM** bagi melindungi autoriti SEO dan backlink indeks.
2. **Soft-Sync State Machine**:
   - `active`: Dipaparkan butang mohon penuh berserta affiliate tracking link.
   - `paused` / `discontinued`: Memaparkan amaran lembut *"⚠️ Status Tawaran: Ditutup Sementara"* dan butang CTA secara automatik mengarahkan pelawat ke hab kategori alternatif aktif.
3. **Auto-Expire Campaigns**: `sync_lifecycle.py` memeriksa tarikh luput `valid_until` promosi sebelum proses binaan statik dijalankan.

---

## 3. Audit Penjejakan Afiliasi (Playwright Verified)

Semua pautan afiliasi diuji secara berkala menggunakan Playwright headless automation:
- **Penyedia Rakan Kongsi**: Involve Asia (RinggitPlus CPA & Experian).
- **Kadar Kejayaan Audit**: 100% 200 OK (0 ralat 404, 0 fallback generik).

---

## 4. Keperluan Persekitaran & Arahan Penggunaan (.env)

Fail konfigurasi rahsia diasingkan ke dalam `.env` (tidak di-commit ke Git):

```bash
# Salin fail templat
cp .env.example .env

# Isi kunci rasmi Cloudflare
CLOUDFLARE_API_TOKEN="cfat_xxx"
CLOUDFLARE_ACCOUNT_ID="e616c381d42b064aed77d093cacba0af"
CLOUDFLARE_ZONE_ID="d9c296b599911752940ae9c9bc111179"
```

### Arahan Binaan Tempatan (Build):
```bash
python3 generator/build_pages.py
```

### Pelaksanaan Audit Playwright:
```bash
python3 generator/audit_playwright.py
```

### Penjadualan Cron Harian (Auto Update):
```cron
# Kemas kini tarikh, status kempen, bina semula dan deploy ke Cloudflare (Setiap 4:00 AM)
0 4 * * * /root/projects/iviz-credit-cards/generator/daily_auto_update.sh
```

---

## 5. Ringkasan Perubahan Terkini (CHANGELOG)

* **feat(master-hub)**: Menambah Master Hub `/kad-kredit.html` dan mengemaskini laluan navigasi navbar & hero CTA.
* **feat(lifecycle)**: Melaksanakan modul `sync_lifecycle.py` untuk menguruskan kitaran hayat promosi dan status produk *paused* tanpa 404.
* **fix(deeplinks)**: Memperbetulkan 44 pautan penjejakan afiliasi RinggitPlus/Involve Asia dan mengesahkannya dengan Playwright.
* **sec(enterprise)**: Menyingkirkan kredensial hardcoded daripada kod sumber kepada persekitaran `.env` berpusat dan membersihkan sejarah commit.

# Dasar Pengurusan Hayat Kad Kredit & Tawaran Bank (Lifecycle Policy)
**Projek**: `iviz-credit-cards` (`cards.iviztrading.com`)  
**Versi**: 2.0 (Dynamic Trend Adaptability & Zero 404 Engine)

---

## 1. Zero 404 Policy (Link Equity Retention)
1. **DILARANG DELETE Halaman Kad Kredit**:
   - Sekiranya kad diberhentikan oleh bank/RinggitPlus, **URL (`/kad/nama-kad.html`) MESTI KEKAL LIVE (HTTP 200)**.
   - Mengelakkan 404 error yang merosakkan kedudukan SEO/AEO/GEO di Google, Perplexity, dan ChatGPT.

2. **Dua Status Utama**:
   - **`active`**: Dipaparkan di grid utama & kalkulator. CTA ke RinggitPlus.
   - **`paused` / `discontinued`**: Banner amaran *"⚠️ Kempen Dijeda"*, CTA ke pautan rasmi bank, & **pautan alternatif automatik** ke 3 kad aktif dalam kategori yang sama.

---

## 2. Dynamic Trend Lifecycle (Perubahan Trend Berbelanja)
Syarat & trend cashback bank kerap berubah mengikut trend semasa (contoh: dari fizikal ke e-Wallet, dari petrol ke pengecasan EV).

1. **Struktur JSON Fleksibel (`data/credit_cards.json`)**:
   - `trending_rank`: Dikemas kini secara automatik mengikut volume carian & kempen RinggitPlus (1–10).
   - `trend_labels`: Tag dinamik yang boleh ditambah mengikut musim (cth: `🔥 Populer 2026`, `⚡ Pengecasan EV`, `🛍️ Kempen Shopee 11.11`).
   - `tier_rules`: Menyokong syarat cashback bertingkat (contoh: 12% Shell jika belanja >RM2.5k, 8% jika >RM1.5k).

2. **Audit & Tarikh Semakan (YMYL Freshness)**:
   - `last_verified`: Rekod tarikh kemaskini terbaharu bagi setiap kad.
   - `source_url`: Pautan rujukan rasmi ke terma bank.
   - Schema JSON-LD menyuntik `dateModified` dinamik untuk isyarat kesegaran data kepada bot AI.

---

## 3. Workflow Auto-Sync & Deployment
- Skrip sync mingguan menyemak status tawaran RinggitPlus melalui Involve Asia API.
- Jika link affiliate tidak lagi menghasilkan komisen, status bertukar ke `paused` tanpa memadam fail HTML.
- Fail `_redirects` dijana secara automatik jika terdapat sebarang pertukaran slug.

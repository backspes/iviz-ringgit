# Panduan & Guardrail Editorial iviz Picks

Dokumen ini adalah rujukan mandatori untuk pembinaan katalog, pengelasan kategori, dan kurasi listicle berasaskan masalah (*Problem-Aware Listicles*) bagi memastikan kualiti portal setanding jenama antarabangsa (Wirecutter, ProductNation).

---

## 1. Format Nama Produk (Standard Editorial)
- **Format**: `[Jenama] [Model / Nama Produk] [Kapasiti / Varian]`
- **CONTOH BETUL**: `Skintific 5X Ceramide Barrier Moisture Gel (30g)`
- **CONTOH SALAH**: `【HOT SALE】Skintific 5X Ceramide Pelembap Wajah Paling Murah 80g [Original KKM]`
- **Peraturan**:
  - Dilarang sama sekali menggunakan perkataan spam marketplace (*Hot Sale, Ready Stock, Original, Fast Delivery, Local Stock, Murah, Viral*).
  - Dilarang menggunakan kurungan cina `【】`, emoji berlebihan, atau tajuk SEMUA HURUF BESAR (ALL CAPS).

---

## 2. Guardrail Kurasi Listicle Berasaskan Masalah (Problem Listicles)
- **PERATURAN UTAMA**: DILARANG SAMA SEKALI menggunakan padanan automatik berasaskan kata kunci / regex (`in text`) untuk senarai masalah!
  - *Sebab*: Padanan regex menyebabkan kesilapan logik seperti `bedak muka (cushion)` dimasukkan ke dalam `sakit pinggang (backrest cushion)`, atau `bekas makanan (vacuum sealer)` dimasukkan ke dalam `vakum bulu kucing`.
- **KAEDAH WAJIB**: Setiap hab masalah **WASPADA DAN HANYA MENGGUNAKAN WHITELIST ID EKSPLISIT** (`PROBLEM_HUB_PRODUCT_IDS` dalam `build_microsites.py`).
- **Prinsip Kurasi**:
  1. *Masalah Kulit Berminyak*: Hanya produk kawalan minyak, BHA/Salicylic Acid, Tea Tree, dan tampalan jerawat.
  2. *Masalah Jeragat & Parut*: Hanya produk bahan pencerah terbukti (Niacinamide, TXA, Vitamin C, Alpha Arbutin).
  3. *Masalah Skin Barrier / Kulit Kering*: Hanya produk pemulihan pelembap pekat (Ceramides, Asid Hialuronik, Lendir Siput).
  4. *Masalah Diet Sihat*: Hanya periuk nasi rendah gula dan penggoreng udara tanpa minyak (Air Fryer).
  5. *Masalah Sakit Pinggang*: Hanya kerusi ergonomik dan kusyen sokongan lumbar.
  6. *Masalah Bulu & Habuk*: Hanya vakum rumah dan penapis udara (Air Purifier).
  7. *Masalah Ruang Kereta*: Hanya aksesori dan pembersih khusus kereta.
  8. *Masalah Pakaian Berkedut*: Hanya seterika wap (Garment Steamer) dan pembuang bulu pakaian (Lint Remover).

---

## 3. Standard Integriti Pautan Afiliasi & Gambar
1. **Zero Homepage Redirect**: Setiap produk mesti mempunyai URL sasaran produk individu sebenar (`i.<shop_id>.<item_id>`) yang dijana melalui Involve Asia Deeplink API (`offer_id=5032`).
2. **CDN Imej Sahih**: Semua imej produk mesti menggunakan pautan CDN Shopee rasmi (`https://cf.shopee.com.my/file/...`) dengan status `HTTP 200`.
3. **Pematuhan SEO / AEO**:
   - Pautan afiliasi wajib: `rel="nofollow noopener sponsored"`.
   - Tiada penyebutan nama platform afiliasi (*Involve Asia, CPA, CPL*) di mana-mana bahagian teks visual atau meta deskripsi.

---

## 4. Semakan Kualiti Sebelum Deployment (Checklist)
Sebelum menolak sebarang kod ke Cloudflare Pages atau GitHub:
- [ ] Jalankan `python3 generator/build_microsites.py` dan pastikan tiada `⚠️ AMARAN ID TIDAK WUJUD`.
- [ ] Sahkan semua halaman mengandungi `<header>` (Nav Bar), `<footer>`, dan skrip burger `toggleNav`.
- [ ] Sahkan `styles.css` statik terjana & tiada amaran CDN dalam console browser.
- [ ] Purge cache zon Cloudflare selepas deploy.

---

## 5. Standard Build Stealth & Kemas (Pematuhan Developer Professional)
- **Tiada CDN Script**: Dilarang menggunakan `<script src="https://cdn.tailwindcss.com"></script>` dalam pengeluaran.
- **Fail CSS Statik**: Semua kelas Tailwind di-compile ke fail statik `dist/styles.css` berasingan via Tailwind CLI.
- **Nyah-Komen HTML**: Semua komen builder/nota internal (`<!-- ... -->`) dibuang secara automatik semasa penjanaan.
- **HTML Minification**: Kod HTML diminify menggunakan `htmlmin` untuk muat turun pantas dan rupa binaan produksi yang bersih.

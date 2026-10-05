import json, os, re, shutil
from datetime import datetime
from components import GLOBAL_HEADER, GLOBAL_FOOTER, GLOBAL_NAV_SCRIPT, apply_global_chrome

# ── setup paths ──────────────────────────────────────────────────────────────
BASE_DIR = "/root/projects/iviz-credit-cards"
DIST_DIR = os.path.join(BASE_DIR, "dist")
DATA_DIR = os.path.join(BASE_DIR, "data")
TODAY = datetime.now().strftime("%Y-%m-%d")

SITE_DOMAIN = "https://ringgit.iviztrading.com"
SITE_NAME = "iviz Ringgit Malaysia"

# Nama bulan dalam Bahasa Malaysia (format tarikh tempatan)
_MONTHS_MS = {
    1: "Januari", 2: "Februari", 3: "Mac", 4: "April", 5: "Mei", 6: "Jun",
    7: "Julai", 8: "Ogos", 9: "September", 10: "Oktober", 11: "November", 12: "Disember",
}
_MONTHS_MS_SHORT = {
    1: "Jan", 2: "Feb", 3: "Mac", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Ogos", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dis",
}


def format_date_ms(value, short=False):
    """Tukar tarikh ISO (YYYY-MM-DD) ke format Malaysia: '5 Oktober 2026'."""
    if not value:
        return "-"
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(value).strip())
    if not m:
        return str(value)
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    name = (_MONTHS_MS_SHORT if short else _MONTHS_MS).get(mo, "")
    return f"{d} {name} {y}"


_now = datetime.now()
MONTH_YEAR = f"{_MONTHS_MS[_now.month]} {_now.year}"
TODAY_MS = f"{_now.day} {_MONTHS_MS[_now.month]} {_now.year}"

# Data Kad Kredit & Pinjaman
cards = json.load(open(os.path.join(DATA_DIR, "credit_cards.json"), encoding="utf-8"))

loans_file = os.path.join(DATA_DIR, "loans.json")
loans = json.load(open(loans_file, encoding="utf-8")) if os.path.exists(loans_file) else []

# Load active promotions
promos_file = os.path.join(DATA_DIR, "promotions.json")
promotions = []
if os.path.exists(promos_file):
    try:
        promotions = [p for p in json.load(open(promos_file, encoding="utf-8")) if p.get("active", True)]
    except Exception:
        promotions = []

active_promo = promotions[0] if promotions else None

# ── KATEGORI KAD KREDIT (Hub-and-Spoke) ────────────────────────────────────────
CATEGORY_META = {
    "petrol": {
        "emoji": "⛽", "title": "Kad Kredit Petrol Terbaik",
        "slug": "kad-kredit-petrol.html",
        "short": "Kad Petrol",
        "desc": "Jimat minyak di Petronas, Shell, Caltex dan BHPetrol dengan pulangan tunai sehingga 12%.",
        "intro": "Halaman ini menyusun kad kredit petrol terbaik di Malaysia untuk tahun 2026. Setiap kad dinilai berdasarkan kadar pulangan tunai sebenar di stesen minyak, syarat gaji minimum, had manfaat bulanan dan yuran tahunan — supaya anda boleh pilih dengan yakin tanpa perlu meneka.",
        "keywords": "kad kredit petrol terbaik, kad kredit petronas, kad kredit shell, rebat minyak",
    },
    "shopping": {
        "emoji": "🛍️", "title": "Kad Kredit Shopping & e-Wallet",
        "slug": "kad-kredit-shopping.html",
        "short": "Kad Shopping",
        "desc": "Pulangan tunai tinggi untuk Shopee, Lazada, TikTok Shop dan tambah nilai e-Wallet.",
        "intro": "Jika anda banyak berbelanja secara dalam talian atau menambah nilai e-Wallet seperti Touch 'n Go, GrabPay dan Boost, kategori ini disusun khas untuk anda. Kad di bawah menawarkan pulangan tunai tertinggi untuk transaksi digital, e-dagang dan bayaran tanpa sentuh.",
        "keywords": "kad kredit shopee, kad kredit online terbaik, kad kredit e-wallet, cashback lazada",
    },
    "all-rounder": {
        "emoji": "💳", "title": "Kad Kredit Cashback All-Rounder",
        "slug": "kad-kredit-cashback.html",
        "short": "Kad Cashback",
        "desc": "Satu kad untuk semua — makan, petrol, barangan dapur dan belanja harian.",
        "intro": "Kad all-rounder sesuai untuk anda yang mahu satu kad sahaja tetapi tetap mendapat pulangan tunai yang baik merentasi pelbagai kategori. Ia biasanya menawarkan kadar rata atau kategori pilihan yang fleksibel setiap bulan.",
        "keywords": "kad kredit cashback terbaik, kad kredit all rounder, kad kredit harian",
    },
    "islamic": {
        "emoji": "🕌", "title": "Kad Kredit Patuh Syariah",
        "slug": "kad-kredit-islamic.html",
        "short": "Kad Syariah",
        "desc": "Bebas riba sepenuhnya (Tawarruq) dengan pulangan tunai dan sumbangan amal.",
        "intro": "Kad kredit patuh Syariah di Malaysia beroperasi berasaskan prinsip Tawarruq, iaitu bebas daripada riba dan unsur-unsur yang tidak dibenarkan. Kategori ini mengumpulkan kad Islamik terbaik yang menawarkan rebat, mata ganjaran dan juga sumbangan amal oleh pihak bank.",
        "keywords": "kad kredit islamik, kad kredit patuh syariah, kad kredit bebas riba",
    },
    "travel": {
        "emoji": "✈️", "title": "Kad Kredit Travel & Air Miles",
        "slug": "kad-kredit-travel.html",
        "short": "Kad Travel",
        "desc": "Kumpul mata penerbangan, akses lounge dan penjimatan perbelanjaan luar negara.",
        "intro": "Untuk anda yang kerap terbang sama ada untuk kerja atau percutian, kad travel mengumpulkan mata ganjaran yang boleh ditukar kepada air miles, akses lounge lapangan terbang dan perlindungan perjalanan. Kategori ini menyenaraikan pilihan terbaik mengikut kadar mata dan manfaat sampingan.",
        "keywords": "kad kredit air miles, kad kredit travel terbaik, kad kredit lounge",
    },
    "gaji": {
        "emoji": "🎓", "title": "Kad Kredit Gaji Permulaan (RM2,000/bulan)",
        "slug": "kad-kredit-gaji-rendah.html",
        "short": "Kad Gaji RM2k",
        "desc": "Pilihan mesra graduan dan pekerja baharu dengan syarat gaji paling rendah.",
        "intro": "Kad kredit untuk gaji rendah di Malaysia kini semakin banyak pilihan. Jika anda graduan baru atau pekerja dengan pendapatan sekitar RM2,000 sebulan, kategori ini menyenaraikan kad yang paling mudah diluluskan, yuran tahunan percuma dan tetap memberi pulangan tunai yang berguna.",
        "keywords": "kad kredit gaji 2000, kad kredit mudah lulus, kad kredit fresh graduate",
    },
}

CATEGORY_ORDER = ["petrol", "shopping", "all-rounder", "islamic", "travel", "gaji"]


# ── KATEGORI PINJAMAN PERIBADI (Hub-and-Spoke) ────────────────────────────────
LOAN_CATEGORY_META = {
    "gaji-rendah": {
        "emoji": "🎓", "title": "Pinjaman Peribadi Gaji Rendah",
        "slug": "pinjaman-gaji-rendah.html",
        "short": "Gaji Rendah",
        "desc": "Kelayakan gaji serendah RM1,500 sebulan — sesuai pekerja swasta dan graduan baharu.",
        "intro": "Kategori ini mengumpulkan pinjaman peribadi dengan syarat kelayakan paling rendah di Malaysia. Jika pendapatan bulanan anda sekitar RM1,500 hingga RM2,000, senarai ini menunjukkan pilihan yang paling mudah diluluskan beserta kadar faedah, jumlah pembiayaan dan had tempoh bayaran balik setiap satu.",
        "keywords": "pinjaman gaji 2000, personal loan gaji rendah, pinjaman mudah lulus",
    },
    "islamic": {
        "emoji": "🕌", "title": "Pinjaman Peribadi Patuh Syariah",
        "slug": "pinjaman-islamic.html",
        "short": "Patuh Syariah",
        "desc": "Pembiayaan Islamik bebas riba berkonsepkan Tawarruq dan Murabahah.",
        "intro": "Pembiayaan peribadi patuh Syariah di Malaysia dikawal selia oleh Bank Negara Malaysia dan bebas daripada unsur riba. Kategori ini menyenaraikan pilihan Islamik terbaik dengan kadar untung tetap, perlindungan takaful dan proses kelulusan yang pantas.",
        "keywords": "pinjaman islamik, pembiayaan peribadi patuh syariah, personal loan bebas riba",
    },
    "pantas": {
        "emoji": "⚡", "title": "Pinjaman Kelulusan Pantas",
        "slug": "pinjaman-kelulusan-pantas.html",
        "short": "Kelulusan Pantas",
        "desc": "Pra-kelulusan sepantas 10 minit hingga 24 jam untuk keperluan segera.",
        "intro": "Apabila anda memerlukan dana segera, masa kelulusan menjadi faktor utama. Kategori ini menyenaraikan pinjaman peribadi yang menawarkan pra-kelulusan dalam talian paling pantas di pasaran — daripada 10 minit hingga 24 jam bekerja — lengkap dengan syarat kelayakan dan had pembiayaan.",
        "keywords": "pinjaman segera 24 jam, personal loan kelulusan pantas, pinjaman cepat lulus",
    },
    "penjawat-awam": {
        "emoji": "🏛️", "title": "Pinjaman untuk Penjawat Awam & GLC",
        "slug": "pinjaman-penjawat-awam.html",
        "short": "Penjawat Awam",
        "desc": "Kadar untung paling rendah dengan potongan gaji ANGKASA dan had tinggi.",
        "intro": "Penjawat awam dan kakitangan GLC menikmati kadar pembiayaan paling kompetitif di pasaran kerana potongan gaji melalui ANGKASA memberi jaminan pembayaran kepada pihak bank. Kategori ini menyenaraikan pilihan terbaik beserta had pembiayaan dan tempoh bayaran balik tertinggi.",
        "keywords": "pinjaman penjawat awam, potongan angkasa, pinjaman glc terbaik",
    },
}

LOAN_CATEGORY_ORDER = ["gaji-rendah", "islamic", "pantas", "penjawat-awam"]


def loan_in_category(loan, cat_key):
    lid = loan["id"]
    feats = " ".join(loan.get("features", [])).lower()
    if cat_key == "gaji-rendah":
        return loan["min_income_monthly"] <= 2000
    if cat_key == "islamic":
        return any(x in lid for x in ("-i", "rajhi", "rakyat", "aeon", "mbsb"))
    if cat_key == "pantas":
        fa = loan["fast_approval"].lower()
        return any(x in fa for x in ("pantas", "10 minit", "24 jam", "segera"))
    if cat_key == "penjawat-awam":
        return any(x in lid for x in ("rakyat", "mbsb")) or "penjawat awam" in feats
    return False


loan_groups = {}
for lk in LOAN_CATEGORY_ORDER:
    loan_groups[lk] = [l for l in loans if loan_in_category(l, lk)]



def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def primary_category_of(card):
    cat = card.get("category", "all-rounder")
    return cat if cat in CATEGORY_META else "all-rounder"


def category_of(card):
    return primary_category_of(card)


# Kumpulkan kad ikut kategori
groups = {}
for c in cards:
    primary = primary_category_of(c)
    groups.setdefault(primary, []).append(c)
    if c["min_income_monthly"] <= 2000:
        groups.setdefault("gaji", []).append(c)


def promo_cta_url(sub: str) -> str:
    if not active_promo:
        return "#"
    base = active_promo.get("cta_url", "#")
    if base.startswith("http"):
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}aff_sub3={sub}"
    return base


def promo_banner_html(is_detail=False, sub="homepage"):
    if not active_promo:
        return ""
    url = promo_cta_url(sub)
    if is_detail:
        return f'''<div class="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-900 border border-amber-500/30 rounded-2xl p-4 text-white flex flex-col md:flex-row items-center justify-between gap-3 shadow-md shadow-amber-500/5 my-4">
            <div class="flex items-center gap-3">
                <span class="bg-amber-400 text-slate-950 font-black text-xs px-2.5 py-1 rounded-full uppercase tracking-wider shrink-0">{active_promo['badge']}</span>
                <p class="text-sm font-semibold text-slate-200">{active_promo['headline']}</p>
            </div>
            <a href="{url}" target="_blank" rel="noopener noreferrer sponsored" class="shrink-0 bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs px-4 py-2 rounded-lg transition-colors">{active_promo['cta_text']}</a>
        </div>'''
    return f'''<div class="bg-slate-950 border-y border-amber-500/30 py-3 px-4 text-white">
        <div class="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left text-xs sm:text-sm">
            <div class="flex items-center gap-2.5">
                <span class="bg-amber-400 text-slate-950 font-black text-[11px] px-2 py-0.5 rounded uppercase tracking-wider">{active_promo['badge']}</span>
                <span class="font-bold text-slate-100">{active_promo['headline']}</span>
            </div>
            <a href="{url}" target="_blank" rel="noopener noreferrer sponsored" class="text-amber-400 font-extrabold hover:underline inline-flex items-center gap-1 shrink-0">{active_promo['cta_text']}</a>
        </div>
    </div>'''


def head(title, desc, canonical_slug="", extra_schema=None, keywords=""):
    canonical_url = f"{SITE_DOMAIN}/{canonical_slug}".rstrip("/")
    schema_graph = [
        {"@type": "WebSite", "@id": f"{SITE_DOMAIN}/#website",
         "url": f"{SITE_DOMAIN}/", "name": SITE_NAME, "inLanguage": "ms-MY"},
        {"@type": "WebPage", "@id": canonical_url,
         "url": canonical_url, "name": title,
         "description": desc, "dateModified": TODAY,
         "isPartOf": {"@id": f"{SITE_DOMAIN}/#website"}},
    ]
    if extra_schema:
        schema_graph.extend(extra_schema)
    schema = {"@context": "https://schema.org", "@graph": schema_graph}
    kw_meta = f'\n    <meta name="keywords" content="{keywords}">' if keywords else ""
    return f'''    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">{kw_meta}
    <link rel="canonical" href="{canonical_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="ms_MY">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
    tailwind.config = {{
        theme: {{ extend: {{
            fontFamily: {{ sans: ['"Plus Jakarta Sans"', 'sans-serif'] }},
            colors: {{
                gold: {{ 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706' }},
                midnight: {{ 900: '#0f172a', 950: '#020617' }}
            }}
        }} }}
    }}
    </script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        html {{ scroll-behavior: smooth; }}
        .card-hover:hover {{ transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.12); }}
        .card-hover {{ transition: transform .2s ease, box-shadow .2s ease; }}
    </style>
    <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'''


def track_apply_url(url: str, slug: str) -> str:
    if not url or not url.startswith("http"):
        return url
    if "invl.me" in url or "invl.us" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}aff_sub4={slug}"


def card_grid_item(c):
    slug = slugify(c["name"])
    islamic_badge = '<span class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-bold px-2 py-0.5 rounded-full">🕌 Syariah</span>' if c["islamic"] else ''
    return f'''<div class="card-hover bg-white rounded-2xl border border-slate-200 p-5 flex flex-col">
                <div class="flex items-center justify-between gap-2 mb-3">
                    <span class="text-xs font-bold text-slate-500">{c['bank']}</span>
                    {islamic_badge}
                </div>
                <img src="{c['image_url']}" alt="Rupa kad {c['name']}" width="180" height="114" loading="lazy"
                     class="rounded-lg border border-slate-200 shadow-sm w-[180px] h-[114px] object-contain bg-white mb-3">
                <h3 class="font-extrabold text-slate-900 leading-snug"><a href="{slug}.html" class="hover:text-amber-600 transition-colors">{c['name']}</a></h3>
                <p class="text-sm text-amber-700 font-bold mt-2 flex-1">🔥 {c['cashback_headline']}</p>
                <div class="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs">
                    <div><div class="text-slate-400 font-semibold">Gaji Min</div><div class="font-bold text-slate-800">RM{c['min_income_monthly']:,}/bln</div></div>
                    <div><div class="text-slate-400 font-semibold">Yuran</div><div class="font-bold text-slate-800 leading-tight">{c['annual_fee'].split('(')[0].strip()}</div></div>
                </div>
                <div class="mt-4 pt-2 grid grid-cols-2 gap-2">
                    <a href="{slug}.html" class="text-center bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs py-2.5 px-3 rounded-xl transition-colors">Ulasan</a>
                    <a href="{track_apply_url(c['apply_url'], slug)}" target="_blank" rel="noopener noreferrer sponsored"
                       class="text-center bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-xs py-2.5 px-3 rounded-xl shadow-sm transition-all whitespace-nowrap">Mohon Terus →</a>
                </div>
            </div>'''


def comparison_table(card_list):
    rows = ""
    for c in card_list:
        slug = slugify(c["name"])
        rows += f'''<tr class="border-b border-slate-100 hover:bg-slate-50">
            <td class="py-3 px-3"><a href="{slug}.html" class="font-bold text-slate-900 hover:text-amber-600">{c['name']}</a><div class="text-xs text-slate-400">{c['bank']}</div></td>
            <td class="py-3 px-3 text-sm text-amber-800 font-semibold">{c['cashback_headline']}</td>
            <td class="py-3 px-3 text-sm text-slate-700 whitespace-nowrap">RM{c['min_income_monthly']:,}</td>
            <td class="py-3 px-3 text-sm text-slate-700">{c['cashback_cap']}</td>
        </tr>'''
    return f'''<div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-left border-collapse min-w-[640px]">
            <thead>
                <tr class="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
                    <th class="py-3 px-3 font-bold">Kad</th>
                    <th class="py-3 px-3 font-bold">Ganjaran Utama</th>
                    <th class="py-3 px-3 font-bold">Gaji Min</th>
                    <th class="py-3 px-3 font-bold">Had Manfaat</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN KAD INDIVIDU (SPOKE)
# ══════════════════════════════════════════════════════════════════════════════
def build_card_page(card):
    slug = slugify(card["name"])
    cat_key = category_of(card)
    cm = CATEGORY_META[cat_key]
    title = f"{card['name']} — Syarat Gaji, Pulangan & Panduan Mohon 2026 | iviz Ringgit"
    desc = f"{card['name']} dari {card['bank']}: {card['cashback_headline']}. Syarat gaji minimum RM{card['min_income_monthly']:,}/bulan. Panduan lengkap kelebihan, had dan cara mohon."

    features_html = "".join(
        f'''<li class="flex items-start gap-3 py-2.5 border-b border-slate-100 last:border-0">
            <span class="text-amber-500 font-bold mt-0.5 shrink-0">✓</span>
            <span class="text-slate-700 leading-relaxed">{f}</span>
        </li>''' for f in card.get("features", [])
    )

    alts = [c for c in cards if c["id"] != card["id"] and category_of(c) == cat_key][:3]
    if len(alts) < 3:
        alts += [c for c in cards if c["id"] != card["id"] and c not in alts][:3 - len(alts)]
    alts_html = "".join(
        f'''<a href="{slugify(a['name'])}.html" class="block p-3 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/50 transition-colors">
            <div class="font-bold text-sm text-slate-900">{a['name']}</div>
            <div class="text-xs text-slate-500 mt-0.5">{a['cashback_headline']}</div>
        </a>''' for a in alts
    )

    faq_items = [
        ("Berapakah syarat gaji minimum untuk memohon " + card["name"] + "?",
         f"Gaji minimum yang diperlukan ialah RM{card['min_income_monthly']:,} sebulan (sekitar RM{card['min_income_annual']:,} setahun). Kad ini sesuai untuk {card['ideal_for'].lower()}"),
        ("Apakah pulangan atau ganjaran utama " + card["name"] + "?",
         f"{card['cashback_headline']}. Had manfaat bulanan ialah {card['cashback_cap']}."),
        ("Adakah " + card["name"] + " mengenakan yuran tahunan?",
         f"Yuran tahunan kad ini ialah {card['annual_fee']}."),
        ("Adakah " + card["name"] + " patuh Syariah?",
         "Ya, kad ini mematuhi prinsip Syariah sepenuhnya (Tawarruq) dan bebas riba." if card["islamic"] else "Tidak. Ini merupakan kad kredit konvensional. Jika anda mahukan pilihan patuh Syariah, lihat kategori Kad Kredit Patuh Syariah kami."),
        ("Apakah perkara penting yang perlu saya ambil perhatian?",
         card["caveats"]),
    ]
    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in faq_items
    )

    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]}
    product_schema = {"@type": "FinancialProduct", "name": card["name"],
        "provider": {"@type": "BankOrCreditUnion", "name": card["bank"]},
        "category": "CreditCard", "feesAndCommissionsSpecification": card["annual_fee"],
        "url": card["source_url"], "description": card["cashback_headline"]}
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": cm["title"], "item": f"{SITE_DOMAIN}/{cm['slug']}"},
        {"@type": "ListItem", "position": 3, "name": card["name"], "item": f"{SITE_DOMAIN}/{slug}.html"}]}

    islamic_badge = '<span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold px-2.5 py-1 rounded-full">🕌 Patuh Syariah</span>' if card["islamic"] else ''

    # ── Lifecycle status (Zero 404 Policy) ──
    status = card.get("status", "active")
    is_paused = status != "active"
    if is_paused:
        paused_notice = '''<div class="bg-amber-50 border border-amber-300 rounded-xl p-4 mb-5 flex items-start gap-3">
                    <span class="text-2xl shrink-0">⚠️</span>
                    <div>
                        <div class="font-extrabold text-amber-900">Tawaran Ditutup Sementara</div>
                        <p class="text-sm text-amber-800 leading-relaxed">Pihak bank sedang mengemas kini tawaran kad ini. Halaman ini dikekalkan untuk rujukan anda — sila semak pilihan alternatif terbaik dalam kategori yang sama di bawah.</p>
                    </div>
                </div>'''
        apply_href = cm['slug']
        apply_label = "Lihat Alternatif Terbaik →"
    else:
        paused_notice = ""
        apply_href = track_apply_url(card['apply_url'], slug)
        apply_label = "Mohon Kad Ini Secara Rasmi →"

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, f"{slug}.html", [product_schema, faq_schema, breadcrumb])}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}

    <main class="flex-1">
        <div class="max-w-6xl mx-auto px-4 pt-6">
            <nav class="text-xs text-slate-500 flex items-center gap-2 flex-wrap">
                <a href="index.html" class="hover:text-amber-500">Utama</a>
                <span>/</span>
                <a href="{cm['slug']}" class="hover:text-amber-500">{cm['emoji']} {cm['title']}</a>
                <span>/</span>
                <span class="text-slate-800 font-semibold">{card['name']}</span>
            </nav>
        </div>

        <section class="max-w-6xl mx-auto px-4 pt-4 pb-4">
            {promo_banner_html(is_detail=True, sub=slug)}
            {paused_notice}
            <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
                <div class="flex flex-col md:flex-row md:items-center gap-6">
                    <div class="shrink-0">
                        <img src="{card['image_url']}" alt="Rupa kad {card['name']}" width="240" height="152" loading="lazy"
                             class="rounded-xl border border-slate-200 shadow-sm w-[240px] max-w-full bg-white">
                    </div>
                    <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-3 mb-3">
                            <span class="bg-slate-900 text-amber-400 border border-slate-800 text-xs font-bold px-3 py-1 rounded-full">{card['bank']}</span>
                            <span class="bg-amber-50 text-amber-800 border border-amber-200 text-xs font-bold px-3 py-1 rounded-full">{cm['emoji']} {card['category_label']}</span>
                            {islamic_badge}
                        </div>
                        <h1 class="text-2xl md:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">{card['name']}</h1>
                        <p class="text-lg text-amber-700 font-bold mt-3">🔥 {card['cashback_headline']}</p>
                        <p class="text-sm text-slate-500 mt-2">Disemak terakhir: {format_date_ms(card['last_verified'])}</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Gaji Minimum</div>
                        <div class="text-lg font-extrabold text-slate-900 mt-1">RM{card['min_income_monthly']:,}<span class="text-xs font-medium text-slate-400">/bln</span></div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Yuran Tahunan</div>
                        <div class="text-sm font-bold text-slate-900 mt-1 leading-tight">{card['annual_fee']}</div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Had Manfaat</div>
                        <div class="text-sm font-bold text-slate-900 mt-1 leading-tight">{card['cashback_cap']}</div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Hari Terbaik</div>
                        <div class="text-sm font-bold text-slate-900 mt-1 leading-tight">{card['cashback_days']}</div>
                    </div>
                </div>

                <a href="{apply_href}" target="_blank" rel="noopener noreferrer sponsored"
                   class="mt-6 block w-full md:w-auto md:inline-block text-center bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold px-8 py-3.5 rounded-xl shadow-lg shadow-amber-500/20 transition-all">
                    {apply_label}
                </a>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-6 pb-10">
            <div class="md:col-span-2 space-y-6">
                <div class="bg-amber-50/60 border border-amber-200/80 rounded-2xl p-5">
                    <h2 class="font-extrabold text-amber-950 mb-2">📌 Ringkasan Pantas</h2>
                    <p class="text-slate-800 leading-relaxed">{card['name']} ialah kad kredit <strong>{card['category_label']}</strong> yang menawarkan <strong>{card['cashback_headline']}</strong>. Ia paling sesuai untuk {card['ideal_for'].lower()} Syarat kelayakan gaji minimum ialah RM{card['min_income_monthly']:,} sebulan, dengan yuran tahunan {card['annual_fee'].lower()}.</p>
                </div>

                <div class="bg-white rounded-2xl border border-slate-200 p-6">
                    <h2 class="text-xl font-extrabold text-slate-900 mb-3">Kelebihan & Ciri-Ciri Utama</h2>
                    <ul>{features_html}</ul>
                </div>

                <div class="bg-rose-50 border border-rose-200 rounded-2xl p-5">
                    <h2 class="font-extrabold text-rose-900 mb-2">⚠️ Perkara Perlu Diambil Perhatian</h2>
                    <p class="text-rose-800 leading-relaxed text-sm">{card['caveats']}</p>
                </div>

                <div class="bg-white rounded-2xl border border-slate-200 p-6">
                    <h2 class="text-xl font-extrabold text-slate-900 mb-4">Soalan Lazim</h2>
                    <div class="space-y-3">{faq_html}</div>
                </div>
            </div>

            <aside class="space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-5 md:sticky md:top-24">
                    <h3 class="font-extrabold text-slate-900 mb-1">Kad Lain dalam Kategori Ini</h3>
                    <a href="{cm['slug']}" class="text-xs font-bold text-amber-600 hover:underline">{cm['emoji']} Lihat semua {len(groups.get(cat_key, []))} kad {cm['short']} →</a>
                    <div class="space-y-2.5 mt-3">{alts_html}</div>
                </div>
                <div class="bg-slate-950 rounded-2xl p-5 text-white border border-slate-800">
                    <h3 class="font-extrabold mb-2 text-amber-400">Bantuan Pengurusan Hutang</h3>
                    <p class="text-sm text-slate-300 leading-relaxed mb-3">Agensi Kaunseling dan Pengurusan Kredit (AKPK) menawarkan khidmat nasihat kewangan percuma.</p>
                    <a href="https://www.akpk.org.my" target="_blank" rel="noopener" class="inline-block bg-amber-400 text-slate-950 font-bold text-sm px-4 py-2 rounded-lg hover:bg-amber-300 transition-colors">Lawati AKPK →</a>
                </div>
            </aside>
        </div>

        <!-- MOBILE STICKY BOTTOM APPLY BAR -->
        <div class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-slate-950/95 backdrop-blur border-t border-slate-800 px-4 py-3 shadow-2xl flex items-center justify-between gap-3">
            <div class="min-w-0 flex-1">
                <div class="text-xs font-extrabold text-white truncate">{card['name']}</div>
                <div class="text-[11px] text-amber-400 font-semibold truncate">{card['cashback_headline']}</div>
            </div>
            <a href="{apply_href}" target="_blank" rel="noopener noreferrer sponsored"
               class="shrink-0 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl shadow-md transition-all">
                {"Mohon Rasmi →" if not is_paused else "Lihat Alternatif →"}
            </a>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN MASTER KAD KREDIT (MASTER HUB / SILO HEAD)
# ══════════════════════════════════════════════════════════════════════════════
def build_master_cards_page():
    nc = len(cards)
    title = f"{nc} Kad Kredit Terbaik Malaysia ({_now.year}) — Bandingkan Rebat & Kelayakan | iviz Ringgit"
    desc = f"Senarai {nc} kad kredit terbaik di Malaysia ({_now.year}). Bandingkan petrol, shopping, cashback harian, patuh syariah, travel dan kelayakan gaji minimum. Panduan permohonan rasmi bank."

    cards_html = "".join(card_grid_item(c) for c in cards)
    table_html = comparison_table(cards)

    # Category pills
    cat_pills = "".join(
        f'''<a href="{CATEGORY_META[k]['slug']}" class="inline-flex items-center gap-2 bg-white hover:bg-amber-50 border border-slate-200 hover:border-amber-400 text-slate-800 hover:text-amber-800 font-bold text-xs px-4 py-2.5 rounded-xl transition-all shadow-sm">
            <span>{CATEGORY_META[k]['emoji']}</span>
            <span>{CATEGORY_META[k]['short']} ({len(groups.get(k, []))})</span>
        </a>'''
        for k in CATEGORY_ORDER if k in groups
    )

    cat_cards_summary = "".join(
        f'''<div class="card-hover bg-white rounded-2xl border border-slate-200 p-5 flex flex-col justify-between">
            <div>
                <div class="text-3xl mb-2">{CATEGORY_META[k]['emoji']}</div>
                <h3 class="font-extrabold text-slate-900 text-base mb-1.5"><a href="{CATEGORY_META[k]['slug']}" class="hover:text-amber-600">{CATEGORY_META[k]['title']}</a></h3>
                <p class="text-xs text-slate-500 leading-relaxed">{CATEGORY_META[k]['desc']}</p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span class="text-xs font-bold text-slate-400">{len(groups.get(k, []))} kad</span>
                <a href="{CATEGORY_META[k]['slug']}" class="text-xs font-extrabold text-amber-600 hover:text-amber-700">Terokai Kategori →</a>
            </div>
        </div>'''
        for k in CATEGORY_ORDER if k in groups
    )

    master_faq = [
        ("Bagaimana cara memilih kad kredit yang paling sesuai di Malaysia?",
         "Kenal pasti corak perbelanjaan bulanan terbesar anda. Jika anda banyak berbelanja petrol kenderaan, pilih kad petrol khas. Sekiranya anda kerap membeli-belah di Shopee/Lazada atau menambah nilai e-Wallet, pilih kad shopping. Untuk kegunaan harian menyeluruh, pilih kad cashback all-rounder atau patuh Syariah."),
        ("Berapakah syarat gaji minimum untuk memohon kad kredit?",
         "Menurut garis panduan Bank Negara Malaysia (BNM), pendapatan tahunan minimum ialah RM24,000 (iaitu RM2,000 sebulan). Terdapat pelbagai kad yang mesra pekerja gaji permulaan dan graduan baharu dalam senarai kami."),
        ("Apakah perbezaan antara kad kredit konvensional dan patuh Syariah?",
         "Kad kredit patuh Syariah beroperasi berasaskan akad Islamik seperti Tawarruq dan bebas daripada sebarang caj riba atau faedah kompaun. Ia juga tidak boleh digunakan di premis tidak patuh Syariah seperti perjudian dan minuman keras."),
        ("Adakah permohonan melalui iviz Ringgit dikenakan sebarang caj?",
         "Tidak sama sekali. Semua perkhidmatan perbandingan di iviz Ringgit adalah 100% percuma. Anda akan diarahkan terus ke portal rasmi institusi perbankan untuk memohon."),
        ("Berapa lama masa yang diambil untuk proses kelulusan pihak bank?",
         "Kebanyakan bank mengambil masa antara 1 hingga 5 hari bekerja selepas dokumen permohonan lengkap diterima. Kad fizikal biasanya dihantar melalui kurier dalam tempoh 7 hingga 14 hari bekerja.")
    ]

    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in master_faq
    )

    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in master_faq]}
    item_list = {"@type": "ItemList", "name": f"{nc} Kad Kredit Terbaik Malaysia ({_now.year})",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["name"],
             "url": f"{SITE_DOMAIN}/{slugify(c['name'])}.html"}
            for i, c in enumerate(cards)]}
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Kad Kredit", "item": f"{SITE_DOMAIN}/kad-kredit.html"}]}

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, f"{SITE_DOMAIN}/kad-kredit.html", [breadcrumb, item_list, faq_schema], "kad kredit terbaik malaysia 2026, bandingkan kad kredit, kad kredit petrol, kad kredit cashback, kad kredit patuh syariah")}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}
{promo_banner_html(is_detail=False, sub="master_cards")}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800 py-12 md:py-16">
            <div class="max-w-6xl mx-auto px-4 text-center">
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-5">📅 Dikemas kini {MONTH_YEAR} · {nc} kad kredit disenaraikan</span>
                <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">💳 {nc} Kad Kredit Terbaik Malaysia ({_now.year})</h1>
                <p class="text-slate-300 text-base md:text-lg mt-4 max-w-3xl mx-auto leading-relaxed">Bandingkan kelayakan gaji minimum, rebat pulangan tunai, had manfaat, dan ganjaran eksklusif setiap kad kredit bank rasmi di Malaysia. Pilih kad mengikut corak perbelanjaan anda.</p>
                <div class="flex flex-wrap items-center justify-center gap-2 mt-6 max-w-4xl mx-auto">
                    {cat_pills}
                </div>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 py-10">
            <div class="mb-12">
                <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-2">Terokai Mengikut Kategori Khas</h2>
                <p class="text-slate-500 text-sm mb-6">Pilih kategori yang tepat untuk melihat perbandingan terperinci dan had ganjaran bulanan.</p>
                <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{cat_cards_summary}</div>
            </div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Senarai Penuh {nc} Kad Kredit Terbaik ({_now.year})</h2>
            <p class="text-slate-500 text-sm mb-6">Pilih kad untuk panduan ulasan lengkap atau klik 'Mohon Terus' ke laman rasmi perbankan.</p>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-14">{cards_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Jadual Perbandingan Keseluruhan</h2>
            <p class="text-slate-500 text-sm mb-6">Bandingkan semua {nc} kad kredit merentasi pelbagai bank dalam satu jadual ringkas.</p>
            <div class="mb-14">{table_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-4">Soalan Lazim Memohon Kad Kredit</h2>
            <div class="space-y-3">{faq_html}</div>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN KATEGORI KAD (HUB)
# ══════════════════════════════════════════════════════════════════════════════
def build_category_page(cat_key):
    cm = CATEGORY_META[cat_key]
    cat_cards = groups.get(cat_key, [])
    n = len(cat_cards)

    title = f"{n} {cm['title']} Malaysia ({_now.year}) — Panduan & Pilihan Terbaik | iviz Ringgit"
    desc = f"Senarai {n} {cm['short'].lower()} terbaik di Malaysia ({_now.year}). {cm['desc']} Bandingkan kelayakan gaji, had pulangan dan rebat tunai."

    cards_html = "".join(card_grid_item(c) for c in cat_cards)
    table_html = comparison_table(cat_cards)

    cheapest = min(cat_cards, key=lambda c: c["min_income_monthly"]) if cat_cards else None
    top = cat_cards[0] if cat_cards else None
    faq_items = []
    if top:
        faq_items.append((f"Apakah {cm['short'].lower()} terbaik di Malaysia pada 2026?",
            f"Antara pilihan utama dalam kategori ini ialah {top['name']} dari {top['bank']}, yang menawarkan {top['cashback_headline']}. Pilihan terbaik bergantung kepada corak perbelanjaan anda — bandingkan jadual di atas untuk melihat had manfaat dan syarat gaji setiap kad."))
    if cheapest:
        faq_items.append((f"Apakah kad dalam kategori ini yang mempunyai syarat gaji paling rendah?",
            f"{cheapest['name']} menawarkan syarat gaji minimum paling rendah dalam kategori ini, iaitu RM{cheapest['min_income_monthly']:,} sebulan (sekitar RM{cheapest['min_income_annual']:,} setahun)."))
    faq_items.append((f"Berapa banyak {cm['short'].lower()} yang disenaraikan di sini?",
        f"Kami menyenaraikan {n} kad dalam kategori ini, disemak berasaskan terma rasmi pihak bank. Senarai dikemas kini secara berkala supaya anda sentiasa melihat pilihan terkini."))
    faq_items.append(("Adakah iviz Ringgit mengenakan sebarang bayaran kepada pengguna?",
        "Tidak. iviz Ringgit ialah portal perbandingan bebas dan kami tidak mengenakan sebarang caj kepada pengguna. Laman ini disokong melalui komisen perkongsian yang dibayar oleh rakan kewangan apabila pengguna memohon melalui pautan kami, tanpa menambah kos kepada anda."))
    faq_items.append(("Bagaimana saya boleh memohon kad ini?",
        "Tekan butang \"Mohon Terus →\" pada kad pilihan anda. Anda akan dibawa terus ke portal rasmi rakan perbankan kami untuk melengkapkan permohonan."))

    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in faq_items
    )

    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]}
    item_list = {"@type": "ItemList", "name": f"{n} {cm['title']} Malaysia ({_now.year})",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["name"],
             "url": f"{SITE_DOMAIN}/{slugify(c['name'])}.html"}
            for i, c in enumerate(cat_cards)]}
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": cm["title"], "item": f"{SITE_DOMAIN}/{cm['slug']}"}]}

    other_cats = "".join(
        f'''<a href="{CATEGORY_META[k]['slug']}" class="block p-3 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/50 transition-colors">
            <div class="font-bold text-sm text-slate-900">{CATEGORY_META[k]['emoji']} {CATEGORY_META[k]['title']}</div>
            <div class="text-xs text-slate-500 mt-0.5">{len(groups.get(k, []))} kad</div>
        </a>''' for k in CATEGORY_ORDER if k != cat_key and k in groups
    )

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, cm['slug'], [faq_schema, item_list, breadcrumb], cm['keywords'])}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}
{promo_banner_html(is_detail=False, sub=cat_key)}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800">
            <div class="max-w-6xl mx-auto px-4 py-12 md:py-16">
                <nav class="text-xs text-slate-400 flex items-center gap-2 mb-6">
                    <a href="index.html" class="hover:text-amber-400">Utama</a>
                    <span>/</span>
                    <span class="text-slate-200 font-semibold">{cm['short']}</span>
                </nav>
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-5">📅 Dikemas kini {MONTH_YEAR} · {n} kad</span>
                <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight max-w-3xl">{cm['emoji']} {n} {cm['title']} Malaysia ({_now.year})</h1>
                <p class="text-slate-300 text-base md:text-lg mt-5 max-w-2xl leading-relaxed">{cm['desc']}</p>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 py-10">
            <div class="bg-amber-50/60 border border-amber-200/80 rounded-2xl p-5 md:p-6 mb-10">
                <h2 class="font-extrabold text-amber-950 mb-2">📌 Ringkasan Pantas</h2>
                <p class="text-slate-800 leading-relaxed">{cm['intro']}</p>
            </div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Senarai {n} {cm['title']} Terbaik ({_now.year})</h2>
            <p class="text-slate-500 text-sm mb-5">Pilih kad untuk panduan penuh atau terus tekan mohon.</p>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{cards_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-1">Jadual Perbandingan</h2>
            <p class="text-slate-500 text-sm mb-5">Bandingkan {n} kad dalam kategori ini pada satu pandangan.</p>
            {table_html}

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-5">Soalan Lazim — {cm['short']}</h2>
            <div class="space-y-3">{faq_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-5">Jelajahi Kategori Lain</h2>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{other_cats}</div>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN PINJAMAN PERIBADI (PERSONAL LOAN HUB)
# ══════════════════════════════════════════════════════════════════════════════
def build_loans_page():
    nloans = len(loans)
    title = f"{nloans} Pinjaman Peribadi Bank Terbaik Malaysia ({_now.year}) — Kadar Rendah & Kelulusan Pantas | iviz Ringgit"
    desc = f"Senarai {nloans} pinjaman peribadi terbaik di Malaysia ({_now.year}): Alliance Bank CashFirst, RHB Personal Financing, AmBank AmMoneyLine dan lain-lain. Bandingkan kadar faedah, syarat gaji dan mohon dalam talian."

    loan_cards_html = ""
    for l in loans:
        slug = l["id"]
        feat_list = "".join(f'<li class="flex items-start gap-2 py-1"><span class="text-amber-500 font-bold">✓</span><span>{f}</span></li>' for f in l.get("features", []))
        loan_cards_html += f'''<div class="card-hover bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between gap-2 mb-2">
                    <span class="bg-slate-900 text-amber-400 font-bold text-xs px-3 py-1 rounded-full">{l['bank']}</span>
                    <span class="text-xs font-semibold text-emerald-600">⚡ {l['fast_approval']}</span>
                </div>
                <h3 class="text-xl font-extrabold text-slate-900 mt-2"><a href="{slug}.html" class="hover:text-amber-600 transition-colors">{l['name']}</a></h3>
                <div class="mt-4 p-4 rounded-xl bg-amber-50/70 border border-amber-200/60">
                    <div class="text-xs text-slate-500 font-semibold">Kadar Faedah</div>
                    <div class="text-lg font-black text-amber-900 mt-0.5">{l['interest_rate']}</div>
                </div>
                <div class="grid grid-cols-2 gap-3 mt-4 text-xs">
                    <div class="p-2.5 bg-slate-50 rounded-lg">
                        <div class="text-slate-400 font-medium">Gaji Minimum</div>
                        <div class="font-bold text-slate-800">RM{l['min_income_monthly']:,}/bln</div>
                    </div>
                    <div class="p-2.5 bg-slate-50 rounded-lg">
                        <div class="text-slate-400 font-medium">Jumlah Pinjaman</div>
                        <div class="font-bold text-slate-800">{l['max_amount']}</div>
                    </div>
                </div>
                <ul class="mt-4 text-xs text-slate-600 space-y-1">{feat_list}</ul>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 gap-2">
                <a href="{slug}.html" class="text-center bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs py-3 px-3 rounded-xl transition-colors">Ulasan</a>
                <a href="{l['apply_url']}" target="_blank" rel="noopener noreferrer sponsored"
                   class="text-center bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-xs py-3 px-3 rounded-xl shadow-md transition-all whitespace-nowrap">
                    Mohon Terus →
                </a>
            </div>
        </div>'''

    loan_cat_pills = "".join(
        f'''<a href="{LOAN_CATEGORY_META[k]['slug']}" class="inline-flex items-center gap-1.5 bg-white hover:bg-amber-50 border border-slate-200 hover:border-amber-400 text-slate-700 text-xs font-bold px-3.5 py-2 rounded-full transition-colors">
            {LOAN_CATEGORY_META[k]['emoji']} {LOAN_CATEGORY_META[k]['short']} <span class="text-amber-600">({len(loan_groups.get(k, []))})</span>
        </a>''' for k in LOAN_CATEGORY_ORDER if loan_groups.get(k)
    )

    loan_faq = [
        ("Apakah syarat asas untuk memohon pinjaman peribadi?",
         "Secara umum, anda perlu berumur 21 tahun ke atas, warganegara Malaysia, dan berpendapatan tetap minimum antara RM2,000 hingga RM3,000 sebulan bergantung kepada pakej bank."),
        ("Berapa lama masa kelulusan pinjaman peribadi?",
         "Kebanyakan bank seperti Alliance Bank dan RHB kini menawarkan pra-kelulusan pantas sepantas 10 minit hingga 24 jam bekerja sekiranya dokumen pendapatan lengkap."),
        ("Adakah pinjaman peribadi ini memerlukan cagaran atau penjamin?",
         "Tidak. Semua pinjaman peribadi yang disenaraikan di atas ialah pinjaman tanpa cagaran (unsecured personal loan) yang tidak memerlukan penjamin."),
        ("Apakah dokumen yang diperlukan semasa permohonan?",
         "Salinan MyKad (depan & belakang), slip gaji 3 bulan terkini, dan penyata KWSP atau penyata bank 3 bulan yang menunjukkan kemasukan gaji.")
    ]
    loan_faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in loan_faq
    )

    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Pinjaman Peribadi", "item": f"{SITE_DOMAIN}/pinjaman-peribadi.html"}]}
    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in loan_faq]}

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, "pinjaman-peribadi.html", [breadcrumb, faq_schema], "pinjaman peribadi terbaik, personal loan malaysia, pinjaman peribadi alliance bank, pinjaman rhb pantas lulus")}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800">
            <div class="max-w-6xl mx-auto px-4 py-14 md:py-18 text-center">
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-6">📅 Dikemas kini {MONTH_YEAR} · {nloans} pinjaman disenaraikan</span>
                <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-3xl mx-auto">{nloans} Pinjaman Peribadi Bank Terbaik Malaysia ({_now.year})</h1>
                <p class="text-slate-300 text-base md:text-lg mt-5 max-w-2xl mx-auto leading-relaxed">Dapatkan tunai segera dengan kadar faedah berpatutan dan kelulusan pantas. Tiada penjamin, tiada cagaran diperlukan.</p>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 py-10">
            <div class="bg-amber-50/60 border border-amber-200/80 rounded-2xl p-5 md:p-6 mb-10">
                <h2 class="font-extrabold text-amber-950 mb-2">📌 Panduan Pantas Pinjaman Peribadi</h2>
                <p class="text-slate-800 leading-relaxed">Pinjaman peribadi adalah pembiayaan tanpa cagaran yang sesuai untuk penyatuan hutang (debt consolidation), modal kecemasan, atau pengubahsuaian rumah. Pastikan anda memilih tempoh bayaran balik yang selaras dengan kemampuan aliran tunai bulanan anda.</p>
            </div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Pilihan Pinjaman Peribadi Disyorkan</h2>
            <p class="text-slate-500 text-sm mb-5">Semak kelayakan dan mohon terus secara dalam talian melalui portal rakan perbankan rasmi.</p>
            <div class="flex flex-wrap gap-2 mb-6">{loan_cat_pills}</div>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">{loan_cards_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-14 mb-4">Soalan Lazim Pinjaman Peribadi</h2>
            <div class="space-y-3">{loan_faq_html}</div>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''



# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN KATEGORI PINJAMAN (HUB LISTICLE)
# ══════════════════════════════════════════════════════════════════════════════
def build_loan_category_page(lk):
    lm = LOAN_CATEGORY_META[lk]
    cat_loans = loan_groups.get(lk, [])
    n = len(cat_loans)

    title = f"{n} {lm['title']} Terbaik Malaysia ({_now.year}) — Panduan & Pilihan | iviz Ringgit"
    desc = f"Senarai {n} {lm['short'].lower()} terbaik di Malaysia ({_now.year}). {lm['desc']} Bandingkan kadar faedah, syarat gaji dan had pembiayaan."

    cards_html = ""
    for l in cat_loans:
        feat_list = "".join(f'<li class="flex items-start gap-2 py-1"><span class="text-amber-500 font-bold">✓</span><span>{f}</span></li>' for f in l.get("features", []))
        cards_html += f'''<div class="card-hover bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between gap-2 mb-2">
                    <span class="bg-slate-900 text-amber-400 font-bold text-xs px-3 py-1 rounded-full">{l['bank']}</span>
                    <span class="text-xs font-semibold text-emerald-600">⚡ {l['fast_approval']}</span>
                </div>
                <h3 class="text-xl font-extrabold text-slate-900 mt-2"><a href="{l['id']}.html" class="hover:text-amber-600 transition-colors">{l['name']}</a></h3>
                <div class="mt-4 p-4 rounded-xl bg-amber-50/70 border border-amber-200/60">
                    <div class="text-xs text-slate-500 font-semibold">Kadar Faedah</div>
                    <div class="text-lg font-black text-amber-900 mt-0.5">{l['interest_rate']}</div>
                </div>
                <div class="grid grid-cols-2 gap-3 mt-4 text-xs">
                    <div class="p-2.5 bg-slate-50 rounded-lg">
                        <div class="text-slate-400 font-medium">Gaji Minimum</div>
                        <div class="font-bold text-slate-800">RM{l['min_income_monthly']:,}/bln</div>
                    </div>
                    <div class="p-2.5 bg-slate-50 rounded-lg">
                        <div class="text-slate-400 font-medium">Jumlah Pinjaman</div>
                        <div class="font-bold text-slate-800">{l['max_amount']}</div>
                    </div>
                </div>
                <ul class="mt-4 text-xs text-slate-600 space-y-1">{feat_list}</ul>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 gap-2">
                <a href="{l['id']}.html" class="text-center bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs py-3 px-3 rounded-xl transition-colors">Ulasan</a>
                <a href="{l['apply_url']}" target="_blank" rel="noopener noreferrer sponsored"
                   class="text-center bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-xs py-3 px-3 rounded-xl shadow-md transition-all whitespace-nowrap">
                    Mohon Terus →
                </a>
            </div>
        </div>'''

    cheapest = min(cat_loans, key=lambda l: l["min_income_monthly"]) if cat_loans else None
    top = cat_loans[0] if cat_loans else None
    faq_items = []
    if top:
        faq_items.append((f"Apakah {lm['short'].lower()} terbaik di Malaysia pada {_now.year}?",
            f"Antara pilihan utama dalam kategori ini ialah {top['name']} dari {top['bank']}, yang menawarkan {top['interest_rate']} dengan {top['fast_approval'].lower()}. Pilihan terbaik bergantung kepada profil pendapatan dan keperluan dana anda."))
    if cheapest:
        faq_items.append(("Apakah pinjaman dalam kategori ini dengan syarat gaji paling rendah?",
            f"{cheapest['name']} menawarkan syarat gaji minimum paling rendah dalam kategori ini, iaitu RM{cheapest['min_income_monthly']:,} sebulan."))
    faq_items.append((f"Berapa banyak pinjaman yang disenaraikan dalam kategori ini?",
        f"Kami menyenaraikan {n} pilihan dalam kategori ini, disemak berasaskan terma rasmi pihak bank. Senarai dikemas kini secara berkala."))
    faq_items.append(("Adakah iviz Ringgit mengenakan sebarang bayaran kepada pengguna?",
        "Tidak. iviz Ringgit ialah portal perbandingan bebas dan kami tidak mengenakan sebarang caj. Laman ini disokong melalui komisen perkongsian yang dibayar oleh rakan kewangan, tanpa menambah kos kepada anda."))
    faq_items.append(("Bagaimana cara memohon pinjaman ini?",
        "Tekan butang \"Mohon Terus →\" pada pilihan anda. Anda akan dibawa terus ke portal rasmi rakan perbankan untuk melengkapkan permohonan."))

    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in faq_items
    )

    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]}
    item_list = {"@type": "ItemList", "name": f"{n} {lm['title']} Terbaik Malaysia ({_now.year})",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": l["name"], "url": f"{SITE_DOMAIN}/{l['id']}.html"}
            for i, l in enumerate(cat_loans)]}
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Pinjaman Peribadi", "item": f"{SITE_DOMAIN}/pinjaman-peribadi.html"},
        {"@type": "ListItem", "position": 3, "name": lm["title"], "item": f"{SITE_DOMAIN}/{lm['slug']}"}]}

    other_cats = "".join(
        f'''<a href="{LOAN_CATEGORY_META[k]['slug']}" class="block p-3 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/50 transition-colors">
            <div class="font-bold text-sm text-slate-900">{LOAN_CATEGORY_META[k]['emoji']} {LOAN_CATEGORY_META[k]['title']}</div>
            <div class="text-xs text-slate-500 mt-0.5">{len(loan_groups.get(k, []))} pinjaman</div>
        </a>''' for k in LOAN_CATEGORY_ORDER if k != lk and loan_groups.get(k)
    )

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, lm['slug'], [faq_schema, item_list, breadcrumb], lm['keywords'])}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800">
            <div class="max-w-6xl mx-auto px-4 py-12 md:py-16">
                <nav class="text-xs text-slate-400 flex items-center gap-2 mb-6 flex-wrap">
                    <a href="index.html" class="hover:text-amber-400">Utama</a>
                    <span>/</span>
                    <a href="pinjaman-peribadi.html" class="hover:text-amber-400">Pinjaman Peribadi</a>
                    <span>/</span>
                    <span class="text-slate-200 font-semibold">{lm['short']}</span>
                </nav>
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-5">📅 Dikemas kini {MONTH_YEAR} · {n} pinjaman</span>
                <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight max-w-3xl">{lm['emoji']} {n} {lm['title']} Terbaik Malaysia ({_now.year})</h1>
                <p class="text-slate-300 text-base md:text-lg mt-5 max-w-2xl leading-relaxed">{lm['desc']}</p>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 py-10">
            <div class="bg-amber-50/60 border border-amber-200/80 rounded-2xl p-5 md:p-6 mb-10">
                <h2 class="font-extrabold text-amber-950 mb-2">📌 Ringkasan Pantas</h2>
                <p class="text-slate-800 leading-relaxed">{lm['intro']}</p>
            </div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Senarai {n} {lm['title']} Terbaik ({_now.year})</h2>
            <p class="text-slate-500 text-sm mb-5">Pilih pinjaman untuk panduan penuh atau terus tekan mohon.</p>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">{cards_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-5">Soalan Lazim — {lm['short']}</h2>
            <div class="space-y-3">{faq_html}</div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-5">Jelajahi Kategori Pinjaman Lain</h2>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{other_cats}</div>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN PINJAMAN INDIVIDU (SPOKE)
# ══════════════════════════════════════════════════════════════════════════════
def build_single_loan_page(loan):
    slug = loan["id"]
    title = f"{loan['name']} — Kadar Faedah, Syarat Kelayakan & Cara Mohon 2026 | iviz Ringgit"
    desc = f"{loan['name']} dari {loan['bank']}: kadar faedah {loan['interest_rate']}, jumlah pinjaman {loan['max_amount']}. Syarat gaji minimum RM{loan['min_income_monthly']:,}/bulan. {loan['fast_approval']}."

    features_html = "".join(
        f'''<li class="flex items-start gap-3 py-2.5 border-b border-slate-100 last:border-0">
            <span class="text-amber-500 font-bold mt-0.5 shrink-0">✓</span>
            <span class="text-slate-700 leading-relaxed">{f}</span>
        </li>''' for f in loan.get("features", [])
    )

    alts = [l for l in loans if l["id"] != loan["id"]][:3]
    alts_html = "".join(
        f'''<a href="{a['id']}.html" class="block p-3 rounded-xl border border-slate-200 hover:border-amber-400 hover:bg-amber-50/50 transition-colors">
            <div class="font-bold text-sm text-slate-900">{a['name']}</div>
            <div class="text-xs text-slate-500 mt-0.5">{a['bank']} · {a['interest_rate']}</div>
        </a>''' for a in alts
    )

    faq_items = [
        ("Berapakah syarat gaji minimum untuk memohon " + loan["name"] + "?",
         f"Gaji minimum yang diperlukan ialah RM{loan['min_income_monthly']:,} sebulan (sekitar RM{loan['min_income_annual']:,} setahun)."),
        ("Berapakah kadar faedah dan had pembiayaan yang ditawarkan?",
         f"Kadar faedah adalah {loan['interest_rate']} dengan jumlah pinjaman {loan['max_amount']}. Tempoh bayaran balik adalah {loan.get('tenure', '1 hingga 7 tahun')}."),
        ("Berapa lama masa kelulusan?",
         f"{loan['fast_approval']}. Permohonan secara dalam talian membolehkan pemprosesan dokumen dilakukan dengan lebih pantas."),
        ("Adakah pinjaman ini memerlukan penjamin?",
         "Tidak. Ini adalah pinjaman peribadi tanpa cagaran (unsecured personal loan) yang tidak memerlukan cagaran atau penjamin.")
    ]
    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in faq_items
    )

    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Pinjaman Peribadi", "item": f"{SITE_DOMAIN}/pinjaman-peribadi.html"},
        {"@type": "ListItem", "position": 3, "name": loan["name"], "item": f"{SITE_DOMAIN}/{slug}.html"}]}
    faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]}
    product_schema = {"@type": "FinancialProduct", "name": loan["name"],
        "provider": {"@type": "BankOrCreditUnion", "name": loan["bank"]},
        "category": "PersonalLoan", "url": loan["source_url"], "description": loan["interest_rate"]}

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, f"{slug}.html", [product_schema, faq_schema, breadcrumb])}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}

    <main class="flex-1">
        <div class="max-w-6xl mx-auto px-4 pt-6">
            <nav class="text-xs text-slate-500 flex items-center gap-2 flex-wrap">
                <a href="index.html" class="hover:text-amber-500">Utama</a>
                <span>/</span>
                <a href="pinjaman-peribadi.html" class="hover:text-amber-500">Pinjaman Peribadi</a>
                <span>/</span>
                <span class="text-slate-800 font-semibold">{loan['name']}</span>
            </nav>
        </div>

        <section class="max-w-6xl mx-auto px-4 pt-4 pb-4">
            <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div class="min-w-0">
                        <div class="flex flex-wrap items-center gap-3 mb-3">
                            <span class="bg-slate-900 text-amber-400 border border-slate-800 text-xs font-bold px-3 py-1 rounded-full">{loan['bank']}</span>
                            <span class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold px-3 py-1 rounded-full">⚡ {loan['fast_approval']}</span>
                        </div>
                        <h1 class="text-2xl md:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">{loan['name']}</h1>
                        <p class="text-lg text-amber-700 font-bold mt-3">🔥 Kadar Faedah: {loan['interest_rate']}</p>
                    </div>
                    <div class="shrink-0">
                        <a href="{loan['apply_url']}" target="_blank" rel="noopener noreferrer sponsored"
                           class="block text-center bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold px-8 py-3.5 rounded-xl shadow-lg shadow-amber-500/20 transition-all">
                            Mohon Pinjaman Rasmi →
                        </a>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Gaji Minimum</div>
                        <div class="text-lg font-extrabold text-slate-900 mt-1">RM{loan['min_income_monthly']:,}<span class="text-xs font-medium text-slate-400">/bln</span></div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Jumlah Pinjaman</div>
                        <div class="text-sm font-bold text-slate-900 mt-1 leading-tight">{loan['max_amount']}</div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Tempoh Pinjaman</div>
                        <div class="text-sm font-bold text-slate-900 mt-1 leading-tight">{loan.get('tenure', '1 - 7 tahun')}</div>
                    </div>
                    <div class="bg-slate-50 rounded-xl p-4">
                        <div class="text-xs text-slate-500 font-semibold">Cagaran / Penjamin</div>
                        <div class="text-sm font-bold text-emerald-600 mt-1 leading-tight">Tiada (Tanpa Cagaran)</div>
                    </div>
                </div>
            </div>
        </section>

        <div class="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-6 pb-10">
            <div class="md:col-span-2 space-y-6">
                <div class="bg-amber-50/60 border border-amber-200/80 rounded-2xl p-5">
                    <h2 class="font-extrabold text-amber-950 mb-2">📌 Ringkasan Pantas</h2>
                    <p class="text-slate-800 leading-relaxed">{loan['name']} dari {loan['bank']} menawarkan pembiayaan peribadi {loan['max_amount']} dengan kadar faedah serendah {loan['interest_rate']}. Pakej ini mempunyai kelebihan seperti {loan['fast_approval'].lower()} dan sesuai untuk pemohon dengan pendapatan minimum RM{loan['min_income_monthly']:,} sebulan.</p>
                </div>

                <div class="bg-white rounded-2xl border border-slate-200 p-6">
                    <h2 class="text-xl font-extrabold text-slate-900 mb-3">Kelebihan & Ciri-Ciri Utama</h2>
                    <ul>{features_html}</ul>
                </div>

                <div class="bg-white rounded-2xl border border-slate-200 p-6">
                    <h2 class="text-xl font-extrabold text-slate-900 mb-4">Soalan Lazim</h2>
                    <div class="space-y-3">{faq_html}</div>
                </div>
            </div>

            <aside class="space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 p-5 md:sticky md:top-24">
                    <h3 class="font-extrabold text-slate-900 mb-1">Pilihan Pinjaman Lain</h3>
                    <a href="pinjaman-peribadi.html" class="text-xs font-bold text-amber-600 hover:underline">Lihat semua {len(loans)} pilihan pinjaman →</a>
                    <div class="space-y-2.5 mt-3">{alts_html}</div>
                </div>
                <div class="bg-slate-950 rounded-2xl p-5 text-white border border-slate-800">
                    <h3 class="font-extrabold mb-2 text-amber-400">Nasihat Kewangan Percuma</h3>
                    <p class="text-sm text-slate-300 leading-relaxed mb-3">Pastikan ansuran bulanan tidak melebihi 40% daripada pendapatan bersih anda. Rujuk AKPK untuk panduan pengurusan kredit berhemah.</p>
                    <a href="https://www.akpk.org.my" target="_blank" rel="noopener" class="inline-block bg-amber-400 text-slate-950 font-bold text-sm px-4 py-2 rounded-lg hover:bg-amber-300 transition-colors">Lawati AKPK →</a>
                </div>
            </aside>
        </div>

        <!-- MOBILE STICKY BOTTOM APPLY BAR -->
        <div class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-slate-950/95 backdrop-blur border-t border-slate-800 px-4 py-3 shadow-2xl flex items-center justify-between gap-3">
            <div class="min-w-0 flex-1">
                <div class="text-xs font-extrabold text-white truncate">{loan['name']}</div>
                <div class="text-[11px] text-amber-400 font-semibold truncate">{loan['interest_rate']}</div>
            </div>
            <a href="{loan['apply_url']}" target="_blank" rel="noopener noreferrer sponsored"
               class="shrink-0 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl shadow-md transition-all">
                Mohon Rasmi →
            </a>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HALAMAN SKOR KREDIT (EXPERIAN)
# ══════════════════════════════════════════════════════════════════════════════
def build_credit_score_page():
    title = "Cara Semak Skor Kredit CCRIS & CTOS Malaysia 2026 — Laporan Rasmi Experian | iviz Ringgit"
    desc = "Ketahui skor kredit CCRIS dan CTOS anda sebelum memohon kad kredit atau pinjaman peribadi. Dapatkan laporan kredit peribadi komprehensif melalui Experian Malaysia secara dalam talian."

    experian_tracking_url = "https://invl.us/aff_m?offer_id=103763&aff_id=122839&source=ia_api_offer&aff_sub1=skor_kredit_page"

    faq_items = [
        ("Apakah itu Skor Kredit dan mengapa ia penting?",
         "Skor kredit ialah nombor 3-digit (biasanya antara 300 hingga 850) yang menunjukkan tahap kebolehpercayaan kewangan anda. Bank dan institusi kewangan menggunakan skor ini untuk meluluskan permohonan kad kredit, pinjaman rumah, dan pinjaman peribadi."),
        ("Apakah perbezaan antara CCRIS dan Experian?",
         "CCRIS diuruskan oleh Bank Negara Malaysia (BNM) dan merekodkan pembayaran hutang anda dengan bank rasmi. Agensi pelaporan kredit seperti Experian menggabungkan rekod CCRIS bersama rekod lain untuk menghasilkan skor kredit yang menyeluruh."),
        ("Bagaimana cara meningkatkan skor kredit yang rendah?",
         "Bayar semua baki kad kredit dan ansuran pinjaman tepat pada masanya setiap bulan, elakkan memohon terlalu banyak kad kredit dalam tempoh singkat, dan pastikan nisbah penggunaan kredit berada di bawah 30% daripada had keseluruhan."),
        ("Adakah semakan skor kredit ini memerlukan pembayaran?",
         "Laporan kredit Experian ialah perkhidmatan berbayar rasmi. Anda akan dimaklumkan tentang yuran sebelum menyelesaikan pembelian di portal rasmi Experian.")
    ]
    faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in faq_items
    )

    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Utama", "item": f"{SITE_DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Semak Skor Kredit", "item": f"{SITE_DOMAIN}/skor-kredit.html"}]}

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, "skor-kredit.html", [breadcrumb], "semak skor kredit, cara semak ctos, cara semak ccris online, experian malaysia")}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800">
            <div class="max-w-6xl mx-auto px-4 py-14 md:py-18 text-center">
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-6">📊 Semakan Kesihatan Kewangan Peribadi</span>
                <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-3xl mx-auto">Ketahui Skor Kredit Anda Sebelum Memohon</h1>
                <p class="text-slate-300 text-base md:text-lg mt-5 max-w-2xl mx-auto leading-relaxed">Tingkatkan peluang kelulusan kad kredit dan pinjaman peribadi dengan menyemak rekod CCRIS dan skor Experian anda secara sah.</p>
            </div>
        </section>

        <div class="max-w-4xl mx-auto px-4 py-10">
            <div class="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-100">
                    <div>
                        <span class="bg-slate-900 text-amber-400 font-extrabold text-xs px-3 py-1 rounded-full">RAKAN RASMI</span>
                        <h2 class="text-2xl font-black text-slate-900 mt-2">Laporan Kredit Peribadi Experian (i-SCORE)</h2>
                        <p class="text-slate-600 text-sm mt-1">Dapatkan salinan laporan kredit lengkap merangkumi rekod CCRIS, litigasi undang-undang dan skor 3-digit.</p>
                    </div>
                    <a href="{experian_tracking_url}" target="_blank" rel="noopener noreferrer sponsored"
                       class="shrink-0 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold text-sm px-6 py-3.5 rounded-xl shadow-md transition-all text-center">
                        Semak Laporan Experian →
                    </a>
                </div>

                <div class="grid sm:grid-cols-3 gap-4 mt-6">
                    <div class="p-4 bg-slate-50 rounded-xl">
                        <div class="text-xl mb-1">📋</div>
                        <div class="font-bold text-slate-900 text-sm">Rekod CCRIS Penuh</div>
                        <div class="text-xs text-slate-500 mt-1">Status bayaran balik pinjaman bank dalam 12 bulan terkini.</div>
                    </div>
                    <div class="p-4 bg-slate-50 rounded-xl">
                        <div class="text-xl mb-1">🎯</div>
                        <div class="font-bold text-slate-900 text-sm">Skor Kredit 3-Digit</div>
                        <div class="text-xs text-slate-500 mt-1">Penilaian gred kredit anda (Sangat Baik, Baik, Sederhana, Lemah).</div>
                    </div>
                    <div class="p-4 bg-slate-50 rounded-xl">
                        <div class="text-xl mb-1">🔒</div>
                        <div class="font-bold text-slate-900 text-sm">Amaran Penipuan</div>
                        <div class="text-xs text-slate-500 mt-1">Kesan sekiranya ada pihak menyalahgunakan identiti MyKad anda.</div>
                    </div>
                </div>
            </div>

            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mt-12 mb-4">Soalan Lazim Skor Kredit</h2>
            <div class="space-y-3">{faq_html}</div>
        </div>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


# ══════════════════════════════════════════════════════════════════════════════
#  HOMEPAGE — Portal Utama iviz Ringgit
# ══════════════════════════════════════════════════════════════════════════════
def build_index():
    title = "iviz Ringgit — Bandingkan Kad Kredit, Pinjaman Peribadi & Skor Kredit Malaysia 2026"
    desc = f"Portal perbandingan kewangan bebas Malaysia: bandingkan {len(cards)} kad kredit, pinjaman peribadi dengan kelulusan pantas, dan semakan skor kredit CCRIS/Experian. Bebas, telus dan tanpa jargon."

    cat_tiles = ""
    for k in CATEGORY_ORDER:
        if k not in groups:
            continue
        cm = CATEGORY_META[k]
        n = len(groups[k])
        preview = "".join(
            f'''<li class="flex items-center gap-2 text-xs text-slate-600">
                <span class="text-amber-500">•</span>
                <a href="{slugify(c['name'])}.html" class="hover:text-amber-700 font-medium truncate">{c['name']}</a>
            </li>''' for c in groups[k][:3]
        )
        cat_tiles += f'''<div class="card-hover bg-white rounded-2xl border border-slate-200 p-6 flex flex-col">
                <div class="text-3xl mb-3">{cm['emoji']}</div>
                <h2 class="text-lg font-extrabold text-slate-900 leading-snug">
                    <a href="{cm['slug']}" class="hover:text-amber-600 transition-colors">{cm['title']}</a>
                </h2>
                <p class="text-sm text-slate-500 mt-2 leading-relaxed flex-1">{cm['desc']}</p>
                <ul class="mt-4 space-y-1.5">{preview}</ul>
                <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                    <span class="text-xs font-bold text-slate-400">{n} kad tersedia</span>
                    <a href="{cm['slug']}" class="text-xs font-extrabold text-amber-600 hover:text-amber-700">Lihat semua →</a>
                </div>
            </div>'''

    featured = cards[:6]
    feat_html = "".join(card_grid_item(c) for c in featured)

    website_schema = {"@type": "WebSite", "@id": f"{SITE_DOMAIN}/#website",
        "url": f"{SITE_DOMAIN}/", "name": SITE_NAME,
        "description": desc, "inLanguage": "ms-MY"}
    collection_schema = {"@type": "CollectionPage", "name": title, "description": desc,
        "url": f"{SITE_DOMAIN}/", "inLanguage": "ms-MY"}

    home_faq = [
        ("Apakah perkhidmatan yang ditawarkan oleh iviz Ringgit?",
         f"iviz Ringgit ialah portal perbandingan kewangan bebas yang membantu rakyat Malaysia membandingkan {len(cards)} kad kredit, pilihan pinjaman peribadi terbaik, dan panduan semakan skor kredit CCRIS/Experian secara telus."),
        ("Adakah permohonan melalui iviz Ringgit dikenakan sebarang caj?",
         "Tidak sama sekali. Semua perkhidmatan perbandingan di iviz Ringgit adalah 100% percuma untuk pengguna."),
        ("Bagaimana cara membuat permohonan kad atau pinjaman?",
         "Pilih produk kewangan yang bersesuaian dengan keperluan anda, semak syarat kelayakan gaji, dan klik butang 'Mohon Terus'. Anda akan dibawa terus ke portal pihak bank atau rakan perbankan rasmi untuk melengkapkan permohonan."),
        ("Adakah maklumat di sini disemak?",
         "Ya. Setiap maklumat disemak berasaskan terma rasmi pihak bank dan Bank Negara Malaysia (BNM), dan tarikh semakan terakhir dipaparkan pada setiap halaman.")
    ]
    home_faq_html = "".join(
        f'''<details class="group border border-slate-200 rounded-xl overflow-hidden bg-white">
            <summary class="cursor-pointer list-none p-4 font-bold text-slate-800 flex justify-between items-center hover:bg-slate-50">
                {q}
                <span class="text-amber-500 text-xl group-open:rotate-45 transition-transform shrink-0 ml-3">+</span>
            </summary>
            <div class="px-4 pb-4 text-slate-600 leading-relaxed text-sm">{a}</div>
        </details>''' for q, a in home_faq
    )
    home_faq_schema = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in home_faq]}

    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(title, desc, "", [website_schema, collection_schema, home_faq_schema], "bandingkan kewangan malaysia, kad kredit terbaik 2026, pinjaman peribadi pantas, semak skor kredit")}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}
{promo_banner_html(is_detail=False, sub="homepage")}

    <main class="flex-1">
        <section class="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white border-b border-slate-800">
            <div class="max-w-6xl mx-auto px-4 py-14 md:py-20 text-center">
                <span class="inline-block bg-slate-800/80 border border-amber-400/30 text-amber-400 text-xs font-bold px-4 py-1.5 rounded-full mb-6">📅 Dikemas kini {MONTH_YEAR} · Hab Kewangan Bebas</span>
                <h1 class="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-3xl mx-auto">Keputusan Kewangan Bijak Untuk Masa Depan Anda</h1>
                <p class="text-slate-300 text-base md:text-lg mt-5 max-w-2xl mx-auto leading-relaxed">Bandingkan kad kredit terbaik mengikut kegunaan sebenar, pinjaman peribadi dengan kelulusan pantas, serta semakan skor kredit rasmi. Telus, tepat dan tanpa caj tersembunyi.</p>
                <div class="flex flex-wrap items-center justify-center gap-3 mt-8">
                    <a href="kad-kredit.html" class="bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-950 font-extrabold px-6 py-3 rounded-xl shadow-lg shadow-amber-500/20 transition-all">💳 Bandingkan Kad Kredit</a>
                    <a href="pinjaman-peribadi.html" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold px-6 py-3 rounded-xl transition-colors">💰 Pinjaman Peribadi</a>
                    <a href="skor-kredit.html" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold px-6 py-3 rounded-xl transition-colors">📊 Semak Skor Kredit</a>
                </div>
            </div>
        </section>

        <section class="max-w-6xl mx-auto px-4 py-12">
            <div class="flex flex-wrap items-end justify-between gap-3 mb-1">
                <h2 class="text-xl md:text-2xl font-extrabold text-slate-900">Pilih Kad Kredit Mengikut Kategori</h2>
                <a href="kad-kredit.html" class="text-sm font-extrabold text-amber-600 hover:text-amber-700">Lihat semua {len(cards)} kad →</a>
            </div>
            <p class="text-slate-500 text-sm mb-6">Tak pasti nak pilih yang mana? Mulakan ikut cara anda guna kad setiap hari — isi minyak, beli-belah, melancong, atau patuh Syariah.</p>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{cat_tiles}</div>
        </section>

        <section class="bg-white border-y border-slate-200">
            <div class="max-w-6xl mx-auto px-4 py-12">
                <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-1">Kad Kredit Pilihan Teratas</h2>
                <p class="text-slate-500 text-sm mb-6">Sebahagian kad paling popular yang disemak oleh pasukan kami.</p>
                <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{feat_html}</div>
            </div>
        </section>

        <section class="max-w-6xl mx-auto px-4 py-12">
            <div class="grid md:grid-cols-2 gap-6">
                <div class="bg-gradient-to-br from-slate-950 to-slate-900 text-white rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
                    <div>
                        <span class="bg-amber-400 text-slate-950 font-bold text-xs px-2.5 py-1 rounded-full">💰 TUNAI PANTAS</span>
                        <h3 class="text-xl font-extrabold text-white mt-3">Perlukan Pinjaman Peribadi?</h3>
                        <p class="text-slate-300 text-sm mt-2 leading-relaxed">Bandingkan tawaran daripada Alliance Bank, RHB dan AmBank dengan kelulusan sepantas 24 jam tanpa penjamin.</p>
                    </div>
                    <div class="mt-6">
                        <a href="pinjaman-peribadi.html" class="inline-block bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs px-5 py-2.5 rounded-xl transition-colors">Lihat Pilihan Pinjaman →</a>
                    </div>
                </div>
                <div class="bg-white rounded-2xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm">
                    <div>
                        <span class="bg-indigo-50 text-indigo-700 font-bold text-xs px-2.5 py-1 rounded-full border border-indigo-200">📊 KESIHATAN KEWANGAN</span>
                        <h3 class="text-xl font-extrabold text-slate-900 mt-3">Semak Skor Kredit CCRIS / Experian</h3>
                        <p class="text-slate-600 text-sm mt-2 leading-relaxed">Ketahui rekod kredit anda sebelum bank membuat penilaian permohonan. Lindungi diri daripada kecurian identiti.</p>
                    </div>
                    <div class="mt-6">
                        <a href="skor-kredit.html" class="inline-block bg-slate-950 hover:bg-slate-800 text-amber-400 font-extrabold text-xs px-5 py-2.5 rounded-xl transition-colors border border-slate-800">Semak Skor Sekarang →</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="max-w-6xl mx-auto px-4 pb-12">
            <h2 class="text-xl md:text-2xl font-extrabold text-slate-900 mb-5">Soalan Lazim</h2>
            <div class="space-y-3">{home_faq_html}</div>
        </section>

        <section class="max-w-6xl mx-auto px-4 py-8">
            <div class="grid md:grid-cols-3 gap-5">
                <div class="bg-white rounded-2xl border border-slate-200 p-5">
                    <div class="text-2xl mb-2">🔍</div>
                    <h3 class="font-extrabold text-slate-900 mb-1">Disemak Berasaskan Fakta</h3>
                    <p class="text-sm text-slate-500 leading-relaxed">Setiap maklumat disemak berasaskan terma rasmi pihak bank dan Bank Negara Malaysia (BNM).</p>
                </div>
                <div class="bg-white rounded-2xl border border-slate-200 p-5">
                    <div class="text-2xl mb-2">⚖️</div>
                    <h3 class="font-extrabold text-slate-900 mb-1">Bebas & Telus</h3>
                    <p class="text-sm text-slate-500 leading-relaxed">Kami tidak mengenakan sebarang caj kepada anda. Setiap kelebihan dan had dipaparkan seadanya.</p>
                </div>
                <div class="bg-white rounded-2xl border border-slate-200 p-5">
                    <div class="text-2xl mb-2">🤝</div>
                    <h3 class="font-extrabold text-slate-900 mb-1">Sokongan AKPK</h3>
                    <p class="text-sm text-slate-500 leading-relaxed">Kami menggalakkan pengurusan kredit berhemah dan merujuk pengguna kepada AKPK bila perlu.</p>
                </div>
            </div>
        </section>
    </main>

{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


def build_trust_page(slug, title, body_html):
    desc = f"{title} — {SITE_NAME}, portal perbandingan kewangan bebas dan telus."
    return f'''<!DOCTYPE html>
<html lang="ms">
<head>
{head(f"{title} | iviz Ringgit", desc, slug)}
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
{GLOBAL_HEADER}
    <main class="flex-1 max-w-3xl mx-auto px-4 py-12">
        <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-10">
            <h1 class="text-2xl md:text-3xl font-extrabold text-slate-900 mb-6">{title}</h1>
            <div class="text-slate-600 leading-relaxed space-y-4">
                {body_html}
            </div>
        </div>
    </main>
{GLOBAL_FOOTER}
{GLOBAL_NAV_SCRIPT}
</body>
</html>'''


TRUST_PAGES = {
    "tentang-kami.html": ("Tentang Kami", """
        <p>iviz Ringgit ialah portal perbandingan kewangan peribadi bebas yang dibina khas untuk rakyat Malaysia. Misi kami mudah: membantu anda membuat keputusan kewangan yang bijak dan telus — sama ada memilih kad kredit mengikut corak berbelanja, mencari pinjaman peribadi berfaedah rendah, atau memantau skor kredit anda.</p>
        <p>Kami percaya maklumat kewangan sepatutnya mudah difahami. Sebab itu setiap panduan kami tulis dalam Bahasa Melayu yang jelas, tanpa jargon industri yang mengelirukan, dan memaparkan kedua-dua kelebihan serta had setiap produk secara jujur.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Apa Yang Kami Lakukan</h2>
        <ul class="list-disc pl-6 space-y-2">
            <li>Menyusun kad kredit mengikut <strong>kegunaan sebenar</strong> (petrol, shopping, e-Wallet, patuh Syariah).</li>
            <li>Membandingkan pinjaman peribadi dengan kelulusan pantas daripada institusi kewangan berlesen.</li>
            <li>Menyediakan panduan semakan dan pemulihan skor kredit bersama agensi pelaporan bertauliah.</li>
        </ul>
        <p>Sebarang pertanyaan boleh dikemukakan melalui halaman <a href="hubungi-kami.html" class="text-amber-600 font-semibold underline">Hubungi Kami</a>.</p>
    """),
    "polisi-editorial.html": ("Polisi Editorial & Ketepatan Maklumat", """
        <p>Kredibiliti adalah asas kepada iviz Ringgit. Polisi ini menerangkan bagaimana kami menyediakan dan menyemak maklumat yang dipaparkan.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Sumber Maklumat</h2>
        <p>Semua maklumat produk kewangan disemak berasaskan terma dan syarat rasmi yang diterbitkan oleh pihak bank serta Bank Negara Malaysia (BNM).</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Kemaskini Berkala</h2>
        <p>Kadar faedah, rebat dan kempen promosi kerap berubah. Kami menyemak semula data secara berkala dan memaparkan tarikh semakan terakhir pada setiap halaman supaya anda tahu tahap ketepatan maklumat tersebut.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Ketelusan Komersial</h2>
        <p>Laman ini disokong melalui komisen perkongsian yang dibayar oleh rakan kewangan apabila pengguna memohon melalui pautan kami. Komisen ini <strong>tidak menambah sebarang kos kepada anda</strong>, dan ia tidak mempengaruhi cara kami menilai sesuatu produk.</p>
    """),
    "penafian-kewangan.html": ("Penafian Kewangan", """
        <p>Maklumat di laman web iviz Ringgit disediakan untuk tujuan maklumat dan pendidikan kewangan umum sahaja. Ia <strong>bukan nasihat kewangan peribadi</strong> dan tidak boleh dianggap sebagai pengesyoran untuk memohon mana-mana produk.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Bukan Institusi Kewangan</h2>
        <p>iviz Ringgit bukan institusi perbankan, pemberi pinjaman, atau penasihat kewangan berlesen. Kami tidak memproses permohonan pinjaman atau kad kredit dan tidak membuat keputusan kelulusan. Semua permohonan diproses sepenuhnya oleh pihak bank atau rakan perbankan berkenaan.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Semak Sebelum Memohon</h2>
        <p>Kadar pulangan, syarat gaji dan terma boleh berubah tanpa notis. Sila rujuk laman web rasmi pihak bank untuk terma terkini sebelum membuat sebarang keputusan kewangan.</p>
        <h2 class="text-lg font-extrabold text-slate-900 pt-2">Pengurusan Hutang Berhemah</h2>
        <p>Kredit ialah alat kewangan yang berkuasa, tetapi ia perlu diurus dengan bijak. Jika anda menghadapi kesukaran mengurus hutang, dapatkan bantuan percuma daripada Agensi Kaunseling dan Pengurusan Kredit (AKPK) di <a href="https://www.akpk.org.my" target="_blank" rel="noopener" class="text-amber-600 font-semibold underline">www.akpk.org.my</a>.</p>
    """),
    "hubungi-kami.html": ("Hubungi Kami", """
        <p>Ada pertanyaan, maklum balas, atau cadangan penambahbaikan untuk iviz Ringgit? Kami ingin mendengar daripada anda.</p>
        <div class="bg-slate-50 rounded-xl p-5 mt-4">
            <p class="text-sm text-slate-500 font-semibold mb-1">E-mel Rasmi</p>
            <p class="text-lg font-extrabold text-slate-900"><a href="mailto:hello@iviztrading.com" class="text-amber-600 hover:underline">hello@iviztrading.com</a></p>
        </div>
        <p class="pt-2">Kami berusaha membalas setiap maklum balas dalam tempoh <strong>1–2 hari bekerja</strong>. Jika anda menghadapi masalah berkaitan hutang kad kredit, sila hubungi AKPK secara terus untuk bantuan segera.</p>
    """),
}


# ── MAIN EXECUTION ────────────────────────────────────────────────────────────
if os.path.exists(DIST_DIR):
    shutil.rmtree(DIST_DIR)
os.makedirs(DIST_DIR, exist_ok=True)

# 1. Halaman kad individu (spoke)
for card in cards:
    slug = slugify(card["name"])
    with open(os.path.join(DIST_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(build_card_page(card))
print(f"Generated {len(cards)} card pages")

# 2. Halaman kategori kad (hub)
with open(os.path.join(DIST_DIR, "kad-kredit.html"), "w", encoding="utf-8") as f:
    f.write(build_master_cards_page())
print("Generated kad-kredit.html (Master Hub)")

cat_slugs = []
for cat_key in CATEGORY_ORDER:
    if cat_key not in groups:
        continue
    cm = CATEGORY_META[cat_key]
    with open(os.path.join(DIST_DIR, cm["slug"]), "w", encoding="utf-8") as f:
        f.write(build_category_page(cat_key))
    cat_slugs.append(cm["slug"])
print(f"Generated {len(cat_slugs)} category pages")

# 3. Halaman Pinjaman Peribadi (Loans Hub, Loan Categories & Spokes)
with open(os.path.join(DIST_DIR, "pinjaman-peribadi.html"), "w", encoding="utf-8") as f:
    f.write(build_loans_page())
print("Generated pinjaman-peribadi.html")

loan_cat_slugs = []
for lk in LOAN_CATEGORY_ORDER:
    if not loan_groups.get(lk):
        continue
    lm = LOAN_CATEGORY_META[lk]
    with open(os.path.join(DIST_DIR, lm["slug"]), "w", encoding="utf-8") as f:
        f.write(build_loan_category_page(lk))
    loan_cat_slugs.append(lm["slug"])
print(f"Generated {len(loan_cat_slugs)} loan category pages")

for l in loans:
    with open(os.path.join(DIST_DIR, f"{l['id']}.html"), "w", encoding="utf-8") as f:
        f.write(build_single_loan_page(l))
print(f"Generated {len(loans)} loan detail pages")

# 4. Halaman Skor Kredit (Experian)
with open(os.path.join(DIST_DIR, "skor-kredit.html"), "w", encoding="utf-8") as f:
    f.write(build_credit_score_page())
print("Generated skor-kredit.html")

# 5. Homepage
with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(build_index())
print("Generated index.html")

# 6. Trust pages
for fn, (t, body) in TRUST_PAGES.items():
    with open(os.path.join(DIST_DIR, fn), "w", encoding="utf-8") as f:
        f.write(build_trust_page(fn, t, body))
print(f"Generated {len(TRUST_PAGES)} trust pages")

# 7. _redirects (elak 404 untuk URL lama /kad/)
redir_lines = [f"/kad/{slugify(c['name'])}.html /{slugify(c['name'])}.html 301" for c in cards]
open(os.path.join(DIST_DIR, "_redirects"), "w", encoding="utf-8").write("\n".join(redir_lines) + "\n")
print("Generated _redirects")

# 8. sitemap
urls = [f"{SITE_DOMAIN}/", f"{SITE_DOMAIN}/kad-kredit.html"] + \
       [f"{SITE_DOMAIN}/{s}" for s in cat_slugs] + \
       [f"{SITE_DOMAIN}/{s}" for s in loan_cat_slugs] + \
       [f"{SITE_DOMAIN}/pinjaman-peribadi.html", f"{SITE_DOMAIN}/skor-kredit.html"] + \
       [f"{SITE_DOMAIN}/{l['id']}.html" for l in loans] + \
       [f"{SITE_DOMAIN}/{slugify(c['name'])}.html" for c in cards] + \
       [f"{SITE_DOMAIN}/{fn}" for fn in TRUST_PAGES]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    prio = "1.0" if u == f"{SITE_DOMAIN}/" else ("0.9" if ("kad-kredit-" in u or "pinjaman" in u or "skor" in u) else "0.8")
    sm += f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{prio}</priority></url>\n'
sm += '</urlset>'
open(os.path.join(DIST_DIR, "sitemap.xml"), "w", encoding="utf-8").write(sm)
print("Generated sitemap.xml")

# 9. robots.txt
open(os.path.join(DIST_DIR, "robots.txt"), "w", encoding="utf-8").write(
    f"User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nSitemap: {SITE_DOMAIN}/sitemap.xml\n"
)
print("Generated robots.txt")

# 10. llms.txt
llms = f"# {SITE_NAME} — Portal Perbandingan Kewangan (Rujukan AI)\n\n"
llms += f"Portal perbandingan kewangan bebas Malaysia: {len(cards)} kad kredit, {len(loans)} pinjaman peribadi kelulusan pantas, dan semakan skor kredit CCRIS/Experian. Dikemas kini {MONTH_YEAR}.\n\n"
llms += "## Hab Produk Kewangan & Pinjaman\n"
llms += f"- Semua Kad Kredit ({len(cards)} kad — Master Hub): {SITE_DOMAIN}/kad-kredit.html\n"
llms += f"- Pinjaman Peribadi (Utama): {SITE_DOMAIN}/pinjaman-peribadi.html\n"
for lk in LOAN_CATEGORY_ORDER:
    if lk in loan_groups:
        lm = LOAN_CATEGORY_META[lk]
        llms += f"- {lm['title']} ({len(loan_groups[lk])} pinjaman): {SITE_DOMAIN}/{lm['slug']}\n"
llms += f"- Semakan Skor Kredit: {SITE_DOMAIN}/skor-kredit.html\n"
for cat_key in CATEGORY_ORDER:
    if cat_key in groups:
        cm = CATEGORY_META[cat_key]
        llms += f"- {cm['title']} ({len(groups[cat_key])} kad): {SITE_DOMAIN}/{cm['slug']}\n"
llms += "\n## Senarai Kad Kredit\n"
for c in cards:
    cm = CATEGORY_META[category_of(c)]
    llms += f"### {c['name']} ({c['bank']})\n- Kategori: {cm['title']}\n- Ganjaran: {c['cashback_headline']}\n- Gaji minimum: RM{c['min_income_monthly']:,}/bulan\n- Yuran: {c['annual_fee']}\n- Had: {c['cashback_cap']}\n- Halaman: {SITE_DOMAIN}/{slugify(c['name'])}.html\n\n"
open(os.path.join(DIST_DIR, "llms.txt"), "w", encoding="utf-8").write(llms)
print("Generated llms.txt")

print(f"\nDONE — {len(urls)} URLs total ({len(cards)} kad + {len(loans)} pinjaman + {len(cat_slugs)} kategori kad + {len(loan_cat_slugs)} kategori pinjaman + 4 trust + 1 utama)")

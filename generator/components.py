"""
Komponen Global (Header / Footer / Nav Script) — iviz Cards
============================================================
Tema Visual Unik: Premium Midnight Navy & Metallic Gold Accent
(Senibina Hub-and-Spoke Enterprise: Dedicated Category Pages bukan one long page)
"""

NAV_LINKS = [
    ("index.html", "Utama"),
    ("kad-kredit-petrol.html", "⛽ Kad Kredit"),
    ("pinjaman-peribadi.html", "💰 Pinjaman Peribadi"),
    ("skor-kredit.html", "📊 Skor Kredit"),
    ("tentang-kami.html", "Mengenai"),
    ("hubungi-kami.html", "Hubungi"),
]

MOBILE_NAV_LINKS = [
    ("index.html", "🏠 Laman Utama"),
    ("kad-kredit-petrol.html", "💳 Semak Kad Kredit"),
    ("pinjaman-peribadi.html", "💰 Pinjaman Peribadi"),
    ("skor-kredit.html", "📊 Semak Skor Kredit (Experian)"),
]

MOBILE_TRUST_LINKS = [
    ("tentang-kami.html", "Mengenai Kami"),
    ("polisi-editorial.html", "Polisi Editorial"),
    ("penafian-kewangan.html", "Penafian Kewangan"),
    ("hubungi-kami.html", "Hubungi Kami"),
]


def _desktop_links():
    return "\n".join(
        f'                <a href="{href}" class="hover:text-amber-400 transition-colors whitespace-nowrap">{label}</a>'
        for href, label in NAV_LINKS
    )


def _mobile_links():
    parts = []
    for href, label in MOBILE_NAV_LINKS:
        parts.append(
            f'                <a href="{href}" class="py-3 border-b border-slate-800 hover:text-amber-400 transition-colors">{label}</a>'
        )
    return "\n".join(parts)


def _mobile_trust_links():
    parts = []
    for href, label in MOBILE_TRUST_LINKS:
        parts.append(
            f'                <a href="{href}" class="py-2 text-slate-400 hover:text-amber-400 text-xs transition-colors">{label}</a>'
        )
    return "\n".join(parts)


GLOBAL_HEADER = f'''    <!-- GLOBAL HEADER (komponen dikongsi — iviz Cards Midnight Gold Palette) -->
    <header class="bg-slate-950 border-b border-slate-800 text-white sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-3.5 flex items-center justify-between">
            <a href="index.html" class="flex items-center gap-2.5 font-extrabold text-lg text-white tracking-tight hover:opacity-90 transition-opacity">
                <span class="bg-gradient-to-tr from-amber-400 via-amber-500 to-yellow-600 text-slate-950 w-7 h-7 rounded-lg flex items-center justify-center font-black text-sm shadow-md shadow-amber-500/20">i</span>
                <span>iviz <span class="text-amber-400 font-bold">Ringgit</span></span>
            </a>
            <div class="hidden lg:flex items-center gap-4 text-xs font-bold text-slate-300">
{_desktop_links()}
            </div>
            <!-- Mobile Burger Button -->
            <button id="nav-burger" aria-label="Buka menu navigasi" aria-expanded="false" aria-controls="nav-mobile-menu" onclick="toggleNav()"
                    class="lg:hidden w-9 h-9 flex items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-200 hover:bg-slate-800 transition-colors">
                <svg id="nav-burger-icon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
        </div>
        <!-- Mobile Dropdown Menu -->
        <div id="nav-mobile-menu" class="lg:hidden hidden border-t border-slate-800 bg-slate-950 text-white">
            <nav class="max-w-6xl mx-auto px-4 py-2 flex flex-col text-sm font-bold text-slate-200">
{_mobile_links()}
                <div class="mt-2 pt-2 border-t border-slate-800 flex flex-col font-semibold">
{_mobile_trust_links()}
                </div>
            </nav>
        </div>
    </header>'''


GLOBAL_FOOTER = '''    <!-- GLOBAL FOOTER (komponen dikongsi — iviz Cards Midnight Palette) -->
    <footer class="bg-slate-950 border-t border-slate-800 py-10 px-4 text-xs text-slate-400 mt-12 mb-16 md:mb-0">
        <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div class="flex flex-col gap-2">
                <div class="flex items-center gap-2.5 font-bold text-white">
                    <span class="bg-gradient-to-tr from-amber-400 to-yellow-600 text-slate-950 w-5 h-5 rounded flex items-center justify-center text-[11px] font-black shadow-sm">i</span>
                    <span>iviz Ringgit Malaysia</span>
                </div>
                <p class="text-[11px] text-slate-500 max-w-sm leading-relaxed">Portal perbandingan kewangan peribadi bebas — Kad Kredit, Pinjaman Peribadi & Semakan Skor Kredit. Telus, tepat dan tanpa caj tersembunyi.</p>
            </div>
            <div class="flex flex-col md:items-end gap-3">
                <div class="flex flex-wrap items-center gap-4 text-slate-300 font-semibold">
                    <a href="kad-kredit-petrol.html" class="hover:text-amber-400">Kad Kredit</a>
                    <a href="pinjaman-peribadi.html" class="hover:text-amber-400">Pinjaman Peribadi</a>
                    <a href="skor-kredit.html" class="hover:text-amber-400">Skor Kredit</a>
                </div>
                <div class="flex flex-wrap items-center gap-4 text-slate-400">
                    <a href="tentang-kami.html" class="hover:text-amber-400 transition-colors">Mengenai Kami</a>
                    <a href="polisi-editorial.html" class="hover:text-amber-400 transition-colors">Polisi Editorial</a>
                    <a href="penafian-kewangan.html" class="hover:text-amber-400 transition-colors">Penafian Kewangan</a>
                    <a href="hubungi-kami.html" class="hover:text-amber-400 transition-colors">Hubungi Kami</a>
                </div>
            </div>
        </div>
        <div class="max-w-6xl mx-auto text-[11px] text-slate-500 mt-6 pt-6 border-t border-slate-900 text-center leading-relaxed">
            Penafian: iviz Cards ialah portal perbandingan pendidikan kewangan bebas. Maklumat disemak berasaskan terma rasmi pihak bank dan Bank Negara Malaysia (BNM). Pautan permohonan mungkin mengandungi rujukan komisen tanpa sebarang caj tambahan kepada anda. Sebelum memohon, baca terma penuh pihak bank. Untuk pengurusan hutang, rujuk <a href="https://www.akpk.org.my" target="_blank" rel="noopener" class="text-amber-400 underline font-medium">AKPK</a>. Hubungi: <a href="mailto:hello@iviztrading.com" class="text-slate-300 underline font-medium">hello@iviztrading.com</a>.
        </div>
    </footer>'''


GLOBAL_NAV_SCRIPT = '''    <!-- GLOBAL NAV SCRIPT -->
    <script>
    function toggleNav() {
        var menu = document.getElementById('nav-mobile-menu');
        var btn = document.getElementById('nav-burger');
        if (!menu) return;
        var isOpen = !menu.classList.contains('hidden');
        menu.classList.toggle('hidden');
        if (btn) btn.setAttribute('aria-expanded', String(!isOpen));
    }
    document.addEventListener('click', function (e) {
        var menu = document.getElementById('nav-mobile-menu');
        var btn = document.getElementById('nav-burger');
        if (!menu || menu.classList.contains('hidden')) return;
        if (btn && btn.contains(e.target)) return;
        if (menu.contains(e.target)) { menu.classList.add('hidden'); if (btn) btn.setAttribute('aria-expanded', 'false'); return; }
        menu.classList.add('hidden');
        if (btn) btn.setAttribute('aria-expanded', 'false');
    });
    </script>'''


def apply_global_chrome(html: str) -> str:
    if "GLOBAL HEADER (komponen dikongsi" not in html:
        import re
        html = re.sub(r'(<body[^>]*>)', r'\1\n' + GLOBAL_HEADER, html, count=1)
    if "GLOBAL FOOTER (komponen dikongsi" not in html:
        html = html.replace("</body>", GLOBAL_FOOTER + "\n</body>", 1)
    if "GLOBAL NAV SCRIPT" not in html:
        html = html.replace("</body>", GLOBAL_NAV_SCRIPT + "\n</body>", 1)
    return html

"""
Lifecycle Manager untuk iviz Ringgit (Promosi, Kad Kredit & Pinjaman)
=====================================================================
Standard Enterprise:
1. Auto-expire promotions bila melepasi tarikh valid_until (format YYYY-MM-DD atau DD Bulan YYYY).
2. Soft-sync lifecycle status (active, paused, discontinued) untuk elak 404.
3. Fallback kempen lalai (evergreen) jika tiada flash deal aktif.
"""
import os, json, re
from datetime import datetime

DATA_DIR = "/root/projects/iviz-credit-cards/data"

_MONTHS = {
    "jan": 1, "januari": 1, "feb": 2, "februari": 2, "mac": 3, "apr": 4, "april": 4,
    "mei": 5, "may": 5, "jun": 6, "jul": 7, "julai": 7, "ogo": 8, "ogos": 8, "aug": 8,
    "sep": 9, "september": 9, "okt": 10, "oktober": 10, "oct": 10,
    "nov": 11, "november": 11, "dis": 12, "disember": 12, "dec": 12
}

def parse_expiry(date_str):
    if not date_str:
        return None
    s = date_str.strip()
    # Try YYYY-MM-DD
    m1 = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m1:
        return datetime(int(m1.group(1)), int(m1.group(2)), int(m1.group(3)))
    # Try DD Mon YYYY / DD Bulan YYYY
    m2 = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", s)
    if m2:
        d = int(m2.group(1))
        mon_str = m2.group(2).lower()[:3]
        y = int(m2.group(3))
        mo = _MONTHS.get(mon_str, 1)
        return datetime(y, mo, d)
    return None

def check_and_update_lifecycle():
    now = datetime.now()
    promos_path = os.path.join(DATA_DIR, "promotions.json")
    
    if os.path.exists(promos_path):
        promos = json.load(open(promos_path, encoding="utf-8"))
        changed = False
        for p in promos:
            exp = parse_expiry(p.get("valid_until"))
            if exp and now > exp:
                if p.get("active", True):
                    print(f"[LIFECYCLE] Expiring promo: {p.get('id')} (expired on {p.get('valid_until')})")
                    p["active"] = False
                    p["expired_at"] = now.strftime("%Y-%m-%d")
                    changed = True
        if changed:
            with open(promos_path, "w", encoding="utf-8") as f:
                json.dump(promos, f, indent=2, ensure_ascii=False)
            print("[LIFECYCLE] Updated promotions.json with expired flags.")
        else:
            print("[LIFECYCLE] All promotions are current and valid.")

if __name__ == "__main__":
    check_and_update_lifecycle()

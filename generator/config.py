"""Pemuatan konfigurasi berpusat — iviz Ringgit.

Semua kredensial dibaca daripada fail .env (tidak pernah disimpan dalam kod
atau di-commit ke repositori). Ini amalan standard enterprise.
"""
import os


def load_env(path=None):
    """Muatkan pembolehubah daripada fail .env ke os.environ."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def require(name):
    """Kembalikan pembolehubah persekitaran wajib atau gagal dengan jelas."""
    load_env()
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Pembolehubah persekitaran '{name}' tidak ditetapkan. Sila isi fail .env.")
    return val

import os, json, requests


def load_env(path):
    """Muatkan kunci daripada fail .env tanpa pendedahan nilai rahsia."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_env(os.path.join(os.path.dirname(__file__), "..", ".env"))

account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
token = os.environ["CLOUDFLARE_API_TOKEN"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 1. Check existing Pages projects
url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects"
res = requests.get(url, headers=headers).json()
print("Existing Pages Projects:")
for p in res.get("result", []):
    print(" -", p.get("name"), "| subdomains:", [d.get("name") for d in p.get("domains", [])])

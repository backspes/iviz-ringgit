import json, requests
from config import require

account_id = require("CLOUDFLARE_ACCOUNT_ID")
zone_id = require("CLOUDFLARE_ZONE_ID")
token = require("CLOUDFLARE_API_TOKEN")
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 1. Create Pages project cards-iviztrading
url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects"
payload = {
    "name": "cards-iviztrading",
    "production_branch": "main",
    "source": {"type": "none"},
}
r = requests.post(url, headers=h, json=payload).json()
print("Create project:", r.get("success"), "|", r.get("errors") or r.get("result", {}).get("name"))

# 2. Add custom domain cards.iviztrading.com
if r.get("success"):
    r2 = requests.post(f"{url}/cards-iviztrading/domains", headers=h, json={"name": "cards.iviztrading.com"}).json()
    print("Add domain:", r2.get("success"), "|", r2.get("errors") or r2.get("result", {}).get("status"))
    # Report required DNS
    if r2.get("result"):
        print("Required DNS:", json.dumps(r2["result"].get("verification_data"), indent=2))

# 3. DNS: ensure CNAME cards -> cards-iviztrading.pages.dev
r3 = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name=cards.iviztrading.com", headers=h).json()
if r3.get("result"):
    print("DNS record exists:", json.dumps(r3["result"], indent=2))
else:
    r4 = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=h, json={
        "type": "CNAME", "name": "cards", "content": "cards-iviztrading.pages.dev",
        "ttl": 1, "proxied": True
    }).json()
    print("DNS created:", r4.get("success"), "|", r4.get("errors") or r4.get("result", {}).get("name"))

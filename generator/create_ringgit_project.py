import json, requests
from config import require

account_id = require("CLOUDFLARE_ACCOUNT_ID")
zone_id = require("CLOUDFLARE_ZONE_ID")
token = require("CLOUDFLARE_API_TOKEN")
h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

PROJECT = "ringgit-iviztrading"
DOMAIN = "ringgit.iviztrading.com"

# 1. Create Pages project
url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects"
payload = {"name": PROJECT, "production_branch": "main", "source": {"type": "none"}}
r = requests.post(url, headers=h, json=payload).json()
print("Create project:", r.get("success"), "|", r.get("errors") or r.get("result", {}).get("name"))

# 2. Add custom domain
r2 = requests.post(f"{url}/{PROJECT}/domains", headers=h, json={"name": DOMAIN}).json()
print("Add domain:", r2.get("success"), "|", r2.get("errors") or r2.get("result", {}).get("status"))

# 3. DNS: CNAME ringgit -> ringgit-iviztrading.pages.dev
r3 = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={DOMAIN}", headers=h).json()
if r3.get("result"):
    print("DNS record already exists:", r3["result"][0]["name"])
else:
    r4 = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=h, json={
        "type": "CNAME", "name": "ringgit", "content": f"{PROJECT}.pages.dev",
        "ttl": 1, "proxied": True
    }).json()
    print("DNS created:", r4.get("success"), "|", r4.get("errors") or r4.get("result", {}).get("name"))

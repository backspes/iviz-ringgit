import json, asyncio, time
from playwright.async_api import async_playwright

async def audit_all():
    cards = json.load(open("/root/projects/iviz-credit-cards/data/credit_cards.json", encoding="utf-8"))
    loans = json.load(open("/root/projects/iviz-credit-cards/data/loans.json", encoding="utf-8"))
    
    items = []
    for c in cards:
        items.append({"type": "card", "id": c["id"], "name": c["name"], "url": c["apply_url"]})
    for l in loans:
        items.append({"type": "loan", "id": l["id"], "name": l["name"], "url": l["apply_url"]})
        
    print(f"Total items to audit: {len(items)} ({len(cards)} cards, {len(loans)} loans)")
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create pool of 4 pages
        semaphore = asyncio.Semaphore(4)
        
        async def check_item(item):
            async with semaphore:
                page = await browser.new_page()
                res = {
                    "type": item["type"],
                    "id": item["id"],
                    "name": item["name"],
                    "url": item["url"],
                    "status": None,
                    "final_url": None,
                    "title": None,
                    "is_404": False,
                    "is_generic": False,
                    "error": None
                }
                try:
                    resp = await page.goto(item["url"], wait_until="domcontentloaded", timeout=25000)
                    res["status"] = resp.status if resp else None
                    res["final_url"] = page.url
                    res["title"] = await page.title()
                    
                    # Check for 404
                    content = await page.content()
                    lower_content = content.lower()
                    lower_title = res["title"].lower()
                    
                    if (res["status"] == 404 or 
                        "404" in lower_title or 
                        "not found" in lower_title or 
                        "page not found" in lower_content or
                        "we can't find that page" in lower_content or
                        "oops! page not found" in lower_content or
                        "halaman tidak dijumpai" in lower_content):
                        res["is_404"] = True
                        
                    # Check if generic landing page
                    if item["type"] == "card":
                        # If ends with /credit-card/ or /credit-cards/ or ringgitplus.com/en/
                        clean_path = res["final_url"].split("?")[0].rstrip("/")
                        if clean_path.endswith("/credit-card") or clean_path.endswith("ringgitplus.com/en"):
                            res["is_generic"] = True
                    elif item["type"] == "loan":
                        clean_path = res["final_url"].split("?")[0].rstrip("/")
                        if clean_path.endswith("/personal-loan") or clean_path.endswith("ringgitplus.com/en"):
                            res["is_generic"] = True
                            
                except Exception as e:
                    res["error"] = str(e)
                finally:
                    await page.close()
                    results.append(res)
                    icon = "❌ 404" if res["is_404"] else ("⚠️ GENERIC" if res["is_generic"] else ("⚠️ ERR" if res["error"] else "✅ OK"))
                    print(f"[{icon}] {res['type'].upper()}: {res['name']} -> {res['final_url'] or res['error']}")
        
        tasks = [check_item(it) for it in items]
        await asyncio.gather(*tasks)
        await browser.close()
        
    with open("/root/projects/iviz-credit-cards/data/playwright_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("\n=== AUDIT SUMMARY ===")
    total = len(results)
    c_404 = [r for r in results if r["is_404"]]
    c_generic = [r for r in results if r["is_generic"]]
    c_err = [r for r in results if r["error"]]
    c_ok = [r for r in results if not r["is_404"] and not r["is_generic"] and not r["error"]]
    
    print(f"Total Checked: {total}")
    print(f"✅ OK (Exact Target Product Page): {len(c_ok)}")
    print(f"❌ 404 Not Found: {len(c_404)}")
    print(f"⚠️ Generic Catalog / Fallback: {len(c_generic)}")
    print(f"⚠️ Network / Timeout Error: {len(c_err)}")
    
    if c_404:
        print("\n--- 404 DETAILS ---")
        for r in c_404:
            print(f"- {r['name']} ({r['type']}): URL={r['url']} => FINAL={r['final_url']} (Title: {r['title']})")
            
    if c_generic:
        print("\n--- GENERIC FALLBACK DETAILS ---")
        for r in c_generic:
            print(f"- {r['name']} ({r['type']}): URL={r['url']} => FINAL={r['final_url']}")

if __name__ == "__main__":
    asyncio.run(audit_all())

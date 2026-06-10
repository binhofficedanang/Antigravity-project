import json

with open("/Users/binhihi/Binhihi Antigravity/audit_results_refined.json", "r", encoding="utf-8") as f:
    results = json.load(f)

print("=== CLEAN SITES FROM AUDIT (200 OK, NO CLOUDFLARE, NO CAPTCHA) ===")
for r in results:
    if r.get("active") and r.get("status_code") == 200:
        if not r.get("cloudflare_detected") and not r.get("captcha_detected"):
            print(f"- {r.get('domain')} ({r.get('site_type')})")

import json
import re

overview_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/overview.txt"

all_sites = set()

with open(overview_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            content = step.get('content', '')
            if not content:
                continue
            
            # Find all domain-looking strings
            domains = re.findall(r'[a-zA-Z0-9.-]+\.(?:com\.vn|com|vn|net|org|edu\.vn)', content)
            for d in domains:
                all_sites.add(d.lower())
        except Exception:
            pass

print("ALL UNIQUE SITES FOUND IN OVERVIEW.TXT:")
ignored = ['google', 'github', 'gemini', 'playwright', 'npm', 'python', 'node', 'microsoft', 'openai', 'localhost', '127.0.0.1']
filtered = []
for s in sorted(all_sites):
    if not any(ig in s for ig in ignored):
        filtered.append(s)

for s in filtered:
    print(f" - {s}")

import re

overview_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/overview.txt"

with open(overview_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Total overview length: {len(content)}")

# Look for domains in the text, e.g. sites ending in .com, .vn, .net
domains = set(re.findall(r'[a-zA-Z0-9.-]+\.(?:com|vn|net|org|edu|info)', content))
print("Found domains in overview.txt:")
for d in sorted(domains):
    if 'gemini' not in d and 'google' not in d and 'playwright' not in d and 'github' not in d:
        print(f" - {d}")

print("\n--- Let's look for sections containing lists of websites ---")
# Find paragraphs or lists containing words like rao vặt, web, site, etc.
lines = content.split('\n')
for idx, line in enumerate(lines):
    if any(keyword in line.lower() for keyword in ["rao vặt", "raovat", "danh sách", "trang web", "kênh rao", "web rao"]):
        print(f"Line {idx}: {line[:120]}")
        # print some context lines
        start = max(0, idx - 5)
        end = min(len(lines), idx + 10)
        print("Context:")
        for i in range(start, end):
            print(f"  {i}: {lines[i]}")
        print("-" * 50)

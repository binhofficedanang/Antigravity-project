overview_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/overview.txt"

with open(overview_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in overview.txt: {len(lines)}")
print("First 20 lines:")
for idx, line in enumerate(lines[:20]):
    print(f"{idx}: {line[:120]}")

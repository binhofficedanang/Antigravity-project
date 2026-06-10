import os

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print("Total lines in log:", len(lines))
    print("First line raw:")
    print(lines[0][:1000] if lines else "Empty")
else:
    print("Log path not found:", log_path)

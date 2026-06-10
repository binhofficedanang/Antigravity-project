import json

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"
domains = [
    "dangtinbatdongsan.vn", "luachonnhadat.vn", "maumau.vn", 
    "chonhadat24h.com", "batdongsangiatot.com.vn", "diaocanphu.com",
    "datviet24h.com.vn", "rongbay.com", "raovat247.net", "nhadat24h.net", 
    "timkiemnhadat.vn", "chothuenha.com.vn", "nhachothue.vn", "bds123.vn"
]

print("=== SEARCHING TRANSCRIPT ===")
user_mentions = []
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = step.get("content", "")
            source = step.get("source", "")
            step_type = step.get("type", "")
            step_idx = step.get("step_index", "")
            
            found = [d for d in domains if d in content]
            if found:
                if source == "USER_EXPLICIT" and step_type == "USER_INPUT":
                    user_mentions.append((step_idx, "USER", found, content))
                elif source == "MODEL" and step_type == "PLANNER_RESPONSE":
                    # Only append model if it explicitly contains decisions like "loại" or "remove" or "disable"
                    if any(kw in content.lower() for kw in ["loại", "remove", "disable", "vô hiệu hóa", "hủy"]):
                        user_mentions.append((step_idx, "MODEL", found, content))
        except Exception as e:
            pass

# Print the last 40 occurrences to see the recent context
for idx, src, f, content in user_mentions[-40:]:
    print(f"\n--- [Step {idx}] By {src} (domains: {f}) ---")
    lines = content.split("\n")
    # print up to 15 lines around the domain mention
    for line in lines:
        if any(d in line for d in f) or any(kw in line.lower() for kw in ["loại", "remove", "disable", "vô hiệu hóa"]):
            print(line[:150])

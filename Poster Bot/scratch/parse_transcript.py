import json
import re

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"
domains = ["dangtinbatdongsan.vn", "luachonnhadat.vn", "maumau.vn", "chonhadat24h.com", "batdongsangiatot.com.vn", "diaocanphu.com"]

print("=== SEARCHING TRANSCRIPT FOR DOMAINS ===")
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            content = step.get("content", "")
            source = step.get("source", "")
            step_type = step.get("type", "")
            step_idx = step.get("step_index", "")
            
            # Check if any domain is mentioned in content
            found = [d for d in domains if d in content]
            if found and source == "USER_EXPLICIT" and step_type == "USER_INPUT":
                print(f"\n[Step {step_idx}] USER REQUEST:")
                print(content)
        except Exception as e:
            pass

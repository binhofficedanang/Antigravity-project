import json

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"
domains = ["alonhadat.com.vn", "mogi.vn", "thongtinnhadat.vn", "batdongsan.net.vn"]

print("=== SEARCHING TRANSCRIPT ===")
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
                    print(f"\n[Step {step_idx}] USER REQUEST (found: {found}):")
                    print(content[:500] + ("..." if len(content) > 500 else ""))
                elif source == "MODEL" and step_type == "PLANNER_RESPONSE" and any(kw in content.lower() for kw in ["loại", "hủy", "fail", "thất bại", "block", "free", "miễn phí"]):
                    print(f"\n[Step {step_idx}] MODEL (found: {found}):")
                    print(content[:500] + ("..." if len(content) > 500 else ""))
        except Exception as e:
            pass

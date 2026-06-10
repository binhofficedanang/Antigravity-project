import json

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            step_idx = step.get("step_index", "")
            if 7100 <= step_idx <= 7235:
                source = step.get("source", "")
                step_type = step.get("type", "")
                content = step.get("content", "")
                if source == "USER_EXPLICIT" and step_type == "USER_INPUT":
                    print(f"\n[Step {step_idx}] USER:")
                    print(content)
                elif source == "MODEL" and step_type == "PLANNER_RESPONSE" and "maumau" in content.lower():
                    print(f"\n[Step {step_idx}] MODEL:")
                    print(content[:500])
        except Exception as e:
            pass

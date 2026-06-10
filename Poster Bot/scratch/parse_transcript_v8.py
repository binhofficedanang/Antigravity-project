import json

log_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            step = json.loads(line)
            step_idx = step.get("step_index", "")
            if 7600 <= step_idx <= 7640:
                source = step.get("source", "")
                content = step.get("content", "")
                if source == "MODEL" and step.get("type") == "PLANNER_RESPONSE":
                    print(f"\n[Step {step_idx}] MODEL RESPONDED:")
                    print(content[:1500])
        except Exception as e:
            pass

import json

transcript_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            # Nếu là output của chạy lệnh run_command
            if step.get('type') == 'RUN_COMMAND' or 'CommandLine' in str(step):
                cmd = step.get('tool_calls', [{}])[0].get('args', {}).get('CommandLine', '')
                if 'main.py' in cmd or 'run_bot' in cmd:
                    print(f"Step {step['step_index']}: {cmd}")
            # In các tin nhắn chứa chữ "thuviennhadat" hoặc "rongbay" hoặc "raovat"
            if 'thuviennhadat' in str(step.get('content', '')).lower():
                print(f"Step {step['step_index']} Message:")
                print(step.get('content')[:300])
                print("-" * 50)
        except Exception:
            pass

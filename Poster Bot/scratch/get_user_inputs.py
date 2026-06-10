import json

transcript_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                step = json.loads(line)
                if step.get('type') == 'USER_INPUT':
                    content = step.get('content', '')
                    if isinstance(content, str):
                        print(f"Step {step.get('step_index')}: {content[:300]}")
                        print("-" * 40)
            except Exception:
                pass
except Exception as e:
    print(f"Error: {e}")

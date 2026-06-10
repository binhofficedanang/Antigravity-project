import json

transcript_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/transcript.jsonl"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        try:
            step = json.loads(line)
            # Tìm xem có chạy commands nào không
            tool_calls = step.get('tool_calls', [])
            for tc in tool_calls:
                if tc.get('name') == 'run_command':
                    cmd = tc.get('arguments', {}).get('CommandLine', '')
                    print(f"Step {step.get('step_index') or i}: {cmd}")
        except Exception as e:
            pass

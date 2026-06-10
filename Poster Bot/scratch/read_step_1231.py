import json

overview_path = "/Users/binhihi/.gemini/antigravity/brain/19fb8242-960b-4344-951b-938cf40ea2d9/.system_generated/logs/overview.txt"

with open(overview_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get('step_index') == 1231:
                content = step.get('content')
                print(f"Content length: {len(content)}")
                # Print from "Các kênh khả thi CÒN LẠI" to the end
                idx = content.find("Các kênh khả thi CÒN LẠI")
                if idx != -1:
                    print(content[idx:idx+1500])
                else:
                    print(content[:1500])
                break
        except Exception as e:
            print("Error parsing", e)

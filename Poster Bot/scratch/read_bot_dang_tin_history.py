import re

filepath = "/Users/binhihi/Binhihi Antigravity/Chat_History_Recovered/Bot_Dang_Tin_BDS_d4e0a976/full_history.md"

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File length: {len(content)}")
    
    # print lines containing .com or .vn
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        if any(kw in line.lower() for kw in ['.com', '.vn', '.net', 'trang', 'web', 'kênh', 'rao vặt']):
            if len(line.strip()) > 5:
                print(f"Line {idx}: {line[:120]}")
except Exception as e:
    print(e)

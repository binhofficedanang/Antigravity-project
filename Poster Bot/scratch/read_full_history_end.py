filepath = "/Users/binhihi/Binhihi Antigravity/Chat_History_Recovered/Bot_Dang_Tin_BDS_d4e0a976/full_history.md"

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # print the last 200 lines
    lines = content.split('\n')
    print(f"Total lines in full_history.md: {len(lines)}")
    for idx in range(max(0, len(lines) - 200), len(lines)):
        print(f"{idx}: {lines[idx]}")
except Exception as e:
    print(e)

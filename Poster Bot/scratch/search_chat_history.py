import os
import re

chat_history_dir = "/Users/binhihi/Binhihi Antigravity/Chat_History_Recovered"
domains = set()

ignored = ['google', 'github', 'gemini', 'playwright', 'npm', 'python', 'node', 'microsoft', 'openai', 'localhost', '127.0.0.1', 'officedanang', 'propertydanang']

for root, dirs, files in os.walk(chat_history_dir):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    found = re.findall(r'[a-zA-Z0-9.-]+\.(?:com\.vn|com|vn|net|org|edu\.vn)', content)
                    for d in found:
                        domains.add(d.lower())
            except Exception as e:
                pass

print("ALL UNIQUE DOMAINS FOUND IN CHAT HISTORY RECOVERED:")
filtered = []
for s in sorted(domains):
    if not any(ig in s for ig in ignored):
        filtered.append(s)

for s in filtered:
    print(f" - {s}")

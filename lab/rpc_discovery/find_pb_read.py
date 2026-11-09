import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\bridge.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

matches = re.finditer(r"conversations", content)
for m in list(matches)[:10]:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 100)
    print("---")
    print(content[start:end])


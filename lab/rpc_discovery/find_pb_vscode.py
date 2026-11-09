import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\vscode\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

matches = re.finditer(r"conversations", content)
count = 0
for m in list(matches):
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 100)
    print("---")
    print(content[start:end])
    count += 1
    if count >= 10:
        break
print("Total found:", count)


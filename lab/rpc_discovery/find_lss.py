import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("LanguageServerService")
while idx != -1:
    print("--- LanguageServerService occurrence ---")
    start = max(0, idx - 100)
    end = min(len(content), idx + 400)
    print(content[start:end])
    idx = content.find("LanguageServerService", idx + 1)


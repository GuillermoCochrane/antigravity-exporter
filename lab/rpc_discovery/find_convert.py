import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("ConvertTrajectoryToMarkdown")
while idx != -1:
    print("--- Match ---")
    start = max(0, idx - 200)
    end = min(len(content), idx + 300)
    print(content[start:end])
    idx = content.find("ConvertTrajectoryToMarkdown", idx + 1)


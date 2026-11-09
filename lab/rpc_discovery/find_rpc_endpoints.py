import re

paths = [
    r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js",
    r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\bridge.js"
]

for p in paths:
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    for m in re.finditer(r"convertTrajectoryToMarkdown", content, re.IGNORECASE):
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + 150)
        print("--- Match in", p)
        print(content[start:end])


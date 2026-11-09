import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

matches = re.finditer(r"convertTrajectoryToMarkdown|getTrajectory|getConversation", content, re.IGNORECASE)
for m in list(matches)[:10]:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 150)
    print("--- RPC call match ---")
    print(content[start:end])


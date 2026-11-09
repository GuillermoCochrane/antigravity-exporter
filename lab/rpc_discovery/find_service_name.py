import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

m = re.search(r'name:\s*"GetTrajectoryTurns".*?typeName:\s*"([^"]+)"', content, re.DOTALL)
if m:
    print("Found GetTrajectoryTurns:", m.group(0)[:300])

# Search for ConnectRPC or service definition with ConvertTrajectoryToMarkdown
for m in re.finditer(r'ConvertTrajectoryToMarkdown', content):
    start = max(0, m.start() - 150)
    end = min(len(content), m.end() + 250)
    print("--- Context ---")
    print(content[start:end])
    break


import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

m = re.search(r'typeName:\s*"[^"]*ConvertTrajectoryToMarkdownRequest[^"]*"', content)
if m:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 200)
    print("Found Request:", content[start:end])
else:
    print("Not found by typeName, searching string ConvertTrajectoryToMarkdownRequest:")
    idx = 0
    for _ in range(5):
        i = content.find("ConvertTrajectoryToMarkdownRequest", idx)
        if i == -1: break
        print(content[max(0, i-50):min(len(content), i+100)])
        idx = i + 1


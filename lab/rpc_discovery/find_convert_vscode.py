import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\vscode\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

matches = [m.start() for m in re.finditer(r"ConvertTrajectoryToMarkdown", content, re.IGNORECASE)]
print(f"Total matches in vscode/extension.js: {len(matches)}")
for idx in matches[:10]:
    print("--- Match at", idx)
    print(content[max(0, idx-100):min(len(content), idx+200)])


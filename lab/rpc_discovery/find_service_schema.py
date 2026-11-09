import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Search for "convertTrajectoryToMarkdown" as a method name in object/service definition
matches = re.finditer(r'convertTrajectoryToMarkdown:\s*\{', content)
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 300)
    print("Method definition:", content[start:end])

# Search for service name: look for `typeName: "exa.` or `typeName: "google.` or similar
for m in re.finditer(r'typeName:\s*"([a-zA-Z0-9_\.]+Service)"', content):
    print("Service found:", m.group(1))


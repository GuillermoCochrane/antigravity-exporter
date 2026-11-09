import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Search for the fields of ConvertTrajectoryToMarkdownRequest or GetCascadeTrajectoryRequest
for term in ["ConvertTrajectoryToMarkdownRequest", "GetCascadeTrajectoryRequest", "GetTrajectoryTurnsRequest"]:
    idx = content.find(term)
    if idx != -1:
        print(f"=== {term} ===")
        print(content[max(0, idx - 100):min(len(content), idx + 400)])


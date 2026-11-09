import re

paths = [
    r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\bridge.js",
    r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js",
    r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\vscode\extension.js"
]

for p in paths:
    print(f"=== Searching in {p} ===")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    matches = re.findall(r".{0,50}(?:\.pb|conversations|Trajectory|trajectory_meta).{0,50}", content)
    print(f"Found {len(matches)} matches")
    for m in matches[:5]:
        print(" ", repr(m))


import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's search for "GetCascadeTrajectoryRequest" or "GetTrajectoryTurnsRequest" in the entire file
for s in ["GetCascadeTrajectoryRequest", "GetTrajectoryTurnsRequest", "ConvertTrajectoryToMarkdownRequest"]:
    matches = [m.start() for m in re.finditer(re.escape(s), content)]
    print(f"Occurrences of {s}: {len(matches)}")
    for pos in matches:
        print("  at", pos, ":", content[max(0, pos-50):min(len(content), pos+150)])


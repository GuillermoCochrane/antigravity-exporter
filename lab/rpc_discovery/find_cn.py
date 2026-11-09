import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# find all occurrences of cN where it's assigned
matches = [m.start() for m in re.finditer(r"\bcN\b", content)]
print(f"Total cN matches: {len(matches)}")
for idx in matches[:10]:
    print("--- Match at", idx)
    print(content[max(0, idx-50):min(len(content), idx+100)])


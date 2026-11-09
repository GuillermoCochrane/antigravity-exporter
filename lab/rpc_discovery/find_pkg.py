import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

m = re.search(r'file_third_party_jetski_[a-zA-Z0-9_]+', content)
if m:
    print("Jetski schema:", m.group(0))

# Search for LanguageServerService in strings
for m in re.finditer(r'"([a-zA-Z0-9_\.]*LanguageServerService)"', content):
    print("Found full service name:", m.group(1))


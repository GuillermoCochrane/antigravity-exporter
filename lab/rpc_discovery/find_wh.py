import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

m = re.search(r"\bwh\s*=\s*\{.*typeName:\s*\"([^\"]+)\"", content)
if m:
    print("Found wh! TypeName:", m.group(1))
    start = max(0, m.start())
    end = min(len(content), m.end() + 1000)
    print(content[start:end])
else:
    # search around 'LanguageServerService'
    idx = content.find('LanguageServerService')
    # search where wh is defined
    for m in re.finditer(r"\bwh\s*=\s*", content):
        print("wh definition:", content[m.start():m.start()+200])


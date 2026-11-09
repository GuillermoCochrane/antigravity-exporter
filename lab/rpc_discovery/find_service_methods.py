import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

m = re.search(r"var\s+cN\s*=|const\s+cN\s*=|let\s+cN\s*=|cN\s*=\s*\{", content)
if m:
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 250)
    print("cN definition:", content[start:end])

# Also search for how requests are made to the daemon
m2 = re.search(r"http://127\.0\.0\.1|localhost:\d+|/exa\.language_server_pb\.", content)
if m2:
    start = max(0, m2.start() - 50)
    end = min(len(content), m2.end() + 250)
    print("Daemon connection:", content[start:end])
else:
    # search for language_server
    m3 = re.search(r"language_server_pb", content)
    if m3:
        start = max(0, m3.start() - 50)
        end = min(len(content), m3.end() + 250)
        print("LS PB:", content[start:end])


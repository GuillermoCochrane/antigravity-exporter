import re

p = r"C:\Users\cochr\AppData\Local\Programs\Antigravity IDE\resources\app\extensions\agy\dist\extension.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

idx = content.find("getRpcClient()")
if idx != -1:
    print("Found getRpcClient():")
    print(content[idx:idx+800])


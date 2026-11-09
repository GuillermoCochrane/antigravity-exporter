import os

PB_PATH = r"C:\Users\cochr\.gemini\antigravity\conversations\630c154e-19b9-4790-acec-1b6d36470dc1.pb"

with open(PB_PATH, "rb") as f:
    h1 = f.read(32)

with open(PB_PATH, "rb") as f:
    h2 = f.read(32)

print("H1 hex:", h1.hex())
print("H2 hex:", h2.hex())
print("Equal?", h1 == h2)

# Check for strings
with open(PB_PATH, "rb") as f:
    sample = f.read(100000)

import re
strings = re.findall(rb'[A-Za-z0-9_ -]{5,}', sample)
print(f"Strings found in 100KB: {len(strings)}")
for s in strings[:10]:
    print(" ", s)


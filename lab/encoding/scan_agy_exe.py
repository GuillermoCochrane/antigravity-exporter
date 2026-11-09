import re

EXE_PATH = r"C:\Users\cochr\.gemini\bin\agy.exe"
print("Scanning agy.exe...")

with open(EXE_PATH, "rb") as f:
    data = f.read()

# Search for conversation file extensions or crypto/compression references
patterns = [
    rb'conversations[/\\][a-zA-Z0-9_-]+\.pb',
    rb'[a-zA-Z0-9_]*Trajectory[a-zA-Z0-9_]*',
    rb'AES[a-zA-Z0-9_-]*',
    rb'chacha[a-zA-Z0-9_-]*',
    rb'zstd',
    rb'snappy',
]

for pat in patterns:
    matches = set(re.findall(pat, data, re.IGNORECASE))
    print(f"Pattern {pat}: {len(matches)} matches")
    for m in list(matches)[:5]:
        print(" ", m)


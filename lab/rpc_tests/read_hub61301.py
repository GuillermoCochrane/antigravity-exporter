import json

with open(r"C:\Users\cochr\.gemini\antigravity\daemon\hub_61301.json", "r") as f:
    data = json.load(f)

print(json.dumps(data, indent=2))


import urllib.request
import json

PORT = 61301
TOKEN = "6687a388-9286-4807-bbb4-73941ea280cc"
CONV_ID = "13768fc6-3fb7-42fb-a498-d1532f97e39b"

url = f"http://127.0.0.1:{PORT}/exa.language_server_pb.LanguageServerService/GetCascadeTrajectory"
body = json.dumps({"cascadeId": CONV_ID}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={
    "Content-Type": "application/json",
    "x-codeium-csrf-token": TOKEN
})

with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode("utf-8"))

traj = data.get("trajectory", {})
steps = traj.get("steps", [])

for s in steps[:4]:
    print("\n================================")
    print(f"Step type: {s.get('type')}")
    print(f"Keys: {list(s.keys())}")
    for k in s:
        if k not in ['metadata', 'type', 'status']:
            print(f"  Field [{k}]:", repr(s[k])[:300])


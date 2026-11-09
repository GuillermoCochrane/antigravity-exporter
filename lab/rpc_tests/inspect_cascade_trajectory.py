import urllib.request
import json

PORT = 61301
TOKEN = "6687a388-9286-4807-bbb4-73941ea280cc"
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"

url = f"http://127.0.0.1:{PORT}/exa.language_server_pb.LanguageServerService/GetCascadeTrajectory"
body = json.dumps({"cascadeId": CONV_ID}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={
    "Content-Type": "application/json",
    "x-codeium-csrf-token": TOKEN
})

with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode("utf-8"))

traj = data.get("trajectory", {})
steps = traj.get("steps", [])
print(f"Total steps returned: {len(steps)}")
print(f"Trajectory ID: {traj.get('trajectoryId')}")
print(f"Cascade ID: {traj.get('cascadeId')}")

# Sample first step, middle step, last step
for i in [0, len(steps)//2, len(steps)-1]:
    if i < len(steps):
        s = steps[i]
        print(f"\n--- Step {i} ---")
        print(f"Type: {s.get('type')}")
        print(f"Status: {s.get('status')}")
        print(f"Created: {s.get('metadata', {}).get('createdAt')}")
        print(f"Keys in step: {list(s.keys())}")
        if 'userInput' in s:
            print("UserInput:", repr(s['userInput'])[:200])
        if 'plannerResponse' in s:
            print("PlannerResponse:", repr(s['plannerResponse'])[:200])


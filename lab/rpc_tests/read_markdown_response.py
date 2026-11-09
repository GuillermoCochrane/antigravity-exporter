import urllib.request
import json

PORT = 61301
TOKEN = "6687a388-9286-4807-bbb4-73941ea280cc"
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"
TRAJ_ID = "c50ae85d-7b35-40bc-af9a-3a767ba74e9b"

url = f"http://127.0.0.1:{PORT}/exa.language_server_pb.LanguageServerService/ConvertTrajectoryToMarkdown"
body = json.dumps({"trajectoryId": TRAJ_ID, "conversationId": CONV_ID}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={
    "Content-Type": "application/json",
    "x-codeium-csrf-token": TOKEN
})

with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode("utf-8"))

md = data.get("markdown", "")
print("Markdown total length:", len(md))
lines = md.split("\n")
print("Total lines:", len(lines))

print("\n--- First 30 lines ---")
for l in lines[:30]:
    print(l)

print("\n--- Last 30 lines ---")
for l in lines[-30:]:
    print(l)


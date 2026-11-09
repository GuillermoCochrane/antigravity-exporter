import urllib.request
import json

PORT = 61301
TOKEN = "6687a388-9286-4807-bbb4-73941ea280cc"
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"

def call_rpc(method, payload):
    url = f"http://127.0.0.1:{PORT}/exa.language_server_pb.LanguageServerService/{method}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-codeium-csrf-token": TOKEN
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            return True, resp.status, data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        return False, e.code, err_body
    except Exception as e:
        return False, 0, str(e)

methods_to_test = [
    ("GetConversationMetadata", {"conversationId": CONV_ID}),
    ("GetCascadeTrajectory", {"trajectoryId": CONV_ID}),
    ("GetCascadeTrajectory", {"cascadeId": CONV_ID}),
    ("GetTrajectoryTurns", {"trajectoryId": CONV_ID}),
    ("ConvertTrajectoryToMarkdown", {"trajectoryId": CONV_ID}),
]

for method, payload in methods_to_test:
    print(f"\n--- Testing {method} with {payload} ---")
    ok, code, res = call_rpc(method, payload)
    print(f"Status: {code} | OK: {ok}")
    print(f"Response: {res[:500]}")


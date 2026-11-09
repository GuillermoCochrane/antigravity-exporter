import urllib.request
import json
import sqlite3

SUMMARIES_DB = r"C:\Users\cochr\.gemini\antigravity\conversation_summaries.db"
PORT = 61301
TOKEN = "6687a388-9286-4807-bbb4-73941ea280cc"

conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()
cursor.execute("SELECT conversation_id, title, preview, step_count FROM conversation_summaries ORDER BY last_modified_time DESC")
convs = cursor.fetchall()
conn.close()

print(f"Total conversations in DB: {len(convs)}")

def get_trajectory(cid):
    url = f"http://127.0.0.1:{PORT}/exa.language_server_pb.LanguageServerService/GetCascadeTrajectory"
    body = json.dumps({"cascadeId": cid}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-codeium-csrf-token": TOKEN
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            traj = data.get("trajectory", {})
            steps = traj.get("steps", [])
            return True, len(steps), traj.get("trajectoryId")
    except Exception as e:
        return False, 0, str(e)

for cid, title, preview, step_count in convs[:10]:
    ok, num_steps, traj_id = get_trajectory(cid)
    name = title if title else preview
    print(f"[{ok}] Conv {cid[:8]}... | Steps in DB: {step_count} | Steps from RPC: {num_steps} | Name: {name[:40]}")


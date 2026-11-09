import os
import sys
import glob
import json
import sqlite3
import urllib.request
import urllib.error
import re
from datetime import datetime

BASE_DIR = r"C:\Users\cochr\.gemini\antigravity"
SUMMARIES_DB = os.path.join(BASE_DIR, "conversation_summaries.db")
DAEMON_DIR = os.path.join(BASE_DIR, "daemon")
OUTPUT_BASE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(OUTPUT_BASE, "output", "raw_json")
MD_DIR = os.path.join(OUTPUT_BASE, "output", "markdown")
CLEAN_DIR = os.path.join(OUTPUT_BASE, "output", "clean_json")

for d in [RAW_DIR, MD_DIR, CLEAN_DIR]:
    os.makedirs(d, exist_ok=True)

def find_active_daemon():
    files = glob.glob(os.path.join(DAEMON_DIR, "hub_*.json"))
    for f in sorted(files, key=os.path.getmtime, reverse=True):
        try:
            with open(f, "r") as jf:
                data = json.load(jf)
            port = data.get("httpPort")
            token = data.get("csrfToken")
            url = f"http://127.0.0.1:{port}"
            req = urllib.request.Request(url, headers={"x-codeium-csrf-token": token})
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    return port, token
        except Exception:
            continue
    raise RuntimeError("No se encontro ningun daemon activo de Antigravity.")

def rpc_call(port, token, method, payload):
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/{method}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-codeium-csrf-token": token
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"RPC {method} fallo ({e.code}): {err}")

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return clean[:60] if clean else "conversacion_sin_titulo"

def extract_clean_messages(steps):
    messages = []
    for s in steps:
        stype = s.get("type", "")
        meta = s.get("metadata", {})
        created_at = meta.get("createdAt")
        
        # parse timestamp
        timestamp = None
        if created_at:
            try:
                # ISO parsing
                dt_str = created_at.split(".")[0].rstrip("Z")
                dt = datetime.fromisoformat(dt_str)
                timestamp = int(dt.timestamp())
            except Exception:
                timestamp = None

        if stype == "CORTEX_STEP_TYPE_USER_INPUT" and "userInput" in s:
            u_text = s["userInput"].get("userResponse") or ""
            if not u_text:
                items = s["userInput"].get("items", [])
                u_text = "\n".join([i.get("text", "") for i in items if i.get("text")])
            
            if u_text.strip():
                messages.append({
                    "id": meta.get("executionId"),
                    "role": "user",
                    "timestamp": timestamp,
                    "text": u_text.strip()
                })

        elif stype == "CORTEX_STEP_TYPE_PLANNER_RESPONSE" and "plannerResponse" in s:
            pr = s["plannerResponse"]
            p_text = pr.get("response") or ""
            if p_text.strip():
                messages.append({
                    "id": pr.get("messageId"),
                    "role": "assistant",
                    "timestamp": timestamp,
                    "text": p_text.strip()
                })
    return messages

print("=== ANTIGRAVITY CONVERSATION EXTRACTOR ===")
port, token = find_active_daemon()
print(f"[OK] Daemon detectado en puerto {port}")

# Test extracting conversation 13768fc6-3fb7-42fb-a498-d1532f97e39b (smaller, fast)
target_id = "13768fc6-3fb7-42fb-a498-d1532f97e39b"
print(f"\nExtrayendo conversacion de prueba: {target_id}...")

traj_data = rpc_call(port, token, "GetCascadeTrajectory", {"cascadeId": target_id})
traj = traj_data.get("trajectory", {})
traj_id = traj.get("trajectoryId")
steps = traj.get("steps", [])
print(f"[OK] Trajectory obtenida: {len(steps)} pasos (trajId: {traj_id})")

# 1. Guardar Raw JSON
raw_file = os.path.join(RAW_DIR, f"{target_id}.raw.json")
with open(raw_file, "w", encoding="utf-8") as f:
    json.dump(traj_data, f, ensure_ascii=False, indent=2)
print(f"[OK] Raw JSON guardado en: {raw_file}")

# 2. Guardar Markdown oficial
try:
    md_data = rpc_call(port, token, "ConvertTrajectoryToMarkdown", {
        "conversationId": target_id,
        "trajectoryId": traj_id
    })
    md_content = md_data.get("markdown", "")
    md_file = os.path.join(MD_DIR, f"{target_id}.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Markdown guardado en: {md_file} ({len(md_content)} chars)")
except Exception as e:
    print(f"[WARN] Error convirtiendo a Markdown con daemon: {e}")

# 3. Guardar Clean JSON (formato chat-exporter)
clean_msgs = extract_clean_messages(steps)
clean_file = os.path.join(CLEAN_DIR, f"{target_id}.clean.json")
with open(clean_file, "w", encoding="utf-8") as f:
    json.dump({
        "id": target_id,
        "trajectoryId": traj_id,
        "messageCount": len(clean_msgs),
        "messages": clean_msgs
    }, f, ensure_ascii=False, indent=2)
print(f"[OK] Clean JSON guardado en: {clean_file} ({len(clean_msgs)} mensajes usuario/asistente)")


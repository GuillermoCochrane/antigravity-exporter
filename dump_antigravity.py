#!/usr/bin/env python3
"""
Antigravity Conversation Dumper & Adapter
Extrae las conversaciones guardadas de Antigravity via ConnectRPC / SQLite
y genera:
  1. Raw JSON (el payload binario decodificado integro)
  2. Clean JSON (formato universal para chat-exporter)
  3. Markdown oficial (renderizado por el propio motor de Antigravity)
"""

import os
import sys
import glob
import json
import sqlite3
import urllib.request
import urllib.error
import re
from datetime import datetime
import argparse

__version__ = "1.0.0"

BASE_DIR = r"C:\Users\cochr\.gemini\antigravity"
SUMMARIES_DB = os.path.join(BASE_DIR, "conversation_summaries.db")
DAEMON_DIR = os.path.join(BASE_DIR, "daemon")
ADAPTER_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_RAW = os.path.join(ADAPTER_DIR, "output", "raw_json")
OUTPUT_CLEAN = os.path.join(ADAPTER_DIR, "output", "clean_json")
OUTPUT_MD = os.path.join(ADAPTER_DIR, "output", "markdown")

def ensure_dirs():
    for d in [OUTPUT_RAW, OUTPUT_CLEAN, OUTPUT_MD]:
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
    raise RuntimeError("No se encontro ningun daemon activo de Antigravity. Asegurate de que el IDE o CLI este abierto.")

def rpc_call(port, token, method, payload):
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/{method}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-codeium-csrf-token": token
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"RPC {method} fallo ({e.code}): {err}")

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    clean = clean.replace(" ", "_")
    return clean[:50] if clean else "conversacion"

def list_conversations():
    if not os.path.exists(SUMMARIES_DB):
        print(f"Error: No se encontro {SUMMARIES_DB}")
        return []
    conn = sqlite3.connect(SUMMARIES_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT conversation_id, title, preview, last_modified_time, step_count, workspace_uris 
        FROM conversation_summaries 
        ORDER BY last_modified_time DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def parse_iso_timestamp(ts_str):
    if not ts_str:
        return None
    try:
        clean = ts_str.split(".")[0].rstrip("Z")
        return int(datetime.fromisoformat(clean).timestamp())
    except Exception:
        return None

def extract_clean_messages(steps):
    messages = []
    for s in steps:
        stype = s.get("type", "")
        meta = s.get("metadata", {})
        created_at = meta.get("createdAt")
        ts = parse_iso_timestamp(created_at)

        if stype == "CORTEX_STEP_TYPE_USER_INPUT" and "userInput" in s:
            u_text = s["userInput"].get("userResponse") or ""
            if not u_text:
                items = s["userInput"].get("items", [])
                u_text = "\n".join([i.get("text", "") for i in items if i.get("text")])
            
            if u_text.strip():
                messages.append({
                    "id": meta.get("executionId") or f"user_{len(messages)}",
                    "role": "user",
                    "timestamp": ts,
                    "text": u_text.strip()
                })

        elif stype == "CORTEX_STEP_TYPE_PLANNER_RESPONSE" and "plannerResponse" in s:
            pr = s["plannerResponse"]
            p_text = pr.get("response") or ""
            if p_text.strip():
                messages.append({
                    "id": pr.get("messageId") or f"bot_{len(messages)}",
                    "role": "assistant",
                    "timestamp": ts,
                    "text": p_text.strip()
                })
    return messages

def export_conversation(port, token, cid, meta_info=None):
    ensure_dirs()
    print(f"\n---> Procesando conversacion: {cid}")
    
    # Obtener trayectoria
    try:
        traj_data = rpc_call(port, token, "GetCascadeTrajectory", {"cascadeId": cid})
    except Exception as e:
        print(f"  [ERROR] No se pudo obtener la trayectoria: {e}")
        return False

    traj = traj_data.get("trajectory", {})
    traj_id = traj.get("trajectoryId")
    steps = traj.get("steps", [])
    print(f"  [OK] Trayectoria recuperada: {len(steps)} pasos")

    # Determinar nombre legible
    title = ""
    date_prefix = ""
    if meta_info:
        title = meta_info.get("title") or meta_info.get("preview") or ""
        last_mod = meta_info.get("last_modified_time", "")
        if last_mod:
            date_prefix = last_mod[:10] + "_"
    
    file_base = f"{date_prefix}{sanitize_filename(title)}_{cid[:8]}"

    # 1. Guardar Raw JSON
    raw_path = os.path.join(OUTPUT_RAW, f"{cid}.raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(traj_data, f, ensure_ascii=False, indent=2)
    print(f"  [1/3] Raw JSON: {os.path.basename(raw_path)}")

    # 2. Guardar Clean JSON
    clean_msgs = extract_clean_messages(steps)
    clean_data = {
        "id": cid,
        "trajectoryId": traj_id,
        "title": title,
        "stepCount": len(steps),
        "messageCount": len(clean_msgs),
        "messages": clean_msgs
    }
    clean_path = os.path.join(OUTPUT_CLEAN, f"{file_base}.clean.json")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"  [2/3] Clean JSON: {os.path.basename(clean_path)} ({len(clean_msgs)} msgs)")

    # 3. Guardar Markdown oficial
    if traj_id:
        try:
            md_res = rpc_call(port, token, "ConvertTrajectoryToMarkdown", {
                "conversationId": cid,
                "trajectoryId": traj_id
            })
            md_content = md_res.get("markdown", "")
            md_path = os.path.join(OUTPUT_MD, f"{file_base}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"  [3/3] Markdown: {os.path.basename(md_path)} ({len(md_content)} chars)")
        except Exception as e:
            print(f"  [WARN] ConvertTrajectoryToMarkdown fallo: {e}")

    return True

def main():
    parser = argparse.ArgumentParser(description="Antigravity Conversation Exporter")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--list", action="store_true", help="Listar todas las conversaciones disponibles")
    parser.add_argument("--id", type=str, help="Exportar una conversacion especifica por ID")
    parser.add_argument("--all", action="store_true", help="Exportar TODAS las conversaciones")
    args = parser.parse_args()

    convs = list_conversations()

    if args.list:
        print(f"\n{'ID':<38} | {'PASOS':<6} | {'FECHA':<10} | {'TITULO / PREVIEW'}")
        print("-" * 90)
        for c in convs:
            cid, title, preview, last_mod, steps, _ = c
            name = (title or preview or "").strip()
            date_str = last_mod[:10] if last_mod else "N/A"
            print(f"{cid:<38} | {steps:<6} | {date_str:<10} | {name[:35]}")
        return

    port, token = find_active_daemon()
    print(f"Conectado a Antigravity Daemon (puerto {port})")

    meta_dict = {c[0]: {"title": c[1], "preview": c[2], "last_modified_time": c[3]} for c in convs}

    if args.id:
        # Match exacto o por prefijo
        matched = [c for c in convs if c[0].startswith(args.id)]
        if not matched:
            print(f"No se encontro ninguna conversacion con ID {args.id}")
            return
        cid = matched[0][0]
        export_conversation(port, token, cid, meta_dict.get(cid))
    elif args.all:
        print(f"Exportando {len(convs)} conversaciones...")
        count = 0
        for c in convs:
            cid = c[0]
            if export_conversation(port, token, cid, meta_dict.get(cid)):
                count += 1
        print(f"\n[FINALIZADO] Se exportaron con exito {count}/{len(convs)} conversaciones.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


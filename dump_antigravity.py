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
import argparse
from core import __version__
from core.discovery import find_active_daemon
from core.database import list_conversations, get_conversations_dict
from core.normalizer import build_clean_conversation
from core.client import get_cascade_trajectory, convert_trajectory_to_markdown
from core.writer import build_file_base, save_raw_json, save_clean_json, save_markdown

def export_conversation(port, token, cid, meta_info=None):
    print(f"\n---> Procesando conversacion: {cid}")
    
    # Obtener trayectoria
    try:
        traj_data = get_cascade_trajectory(port, token, cid)
    except Exception as e:
        print(f"  [ERROR] No se pudo obtener la trayectoria: {e}")
        return False

    traj = traj_data.get("trajectory", {})
    traj_id = traj.get("trajectoryId")
    steps = traj.get("steps", [])
    print(f"  [OK] Trayectoria recuperada: {len(steps)} pasos")

    title = (meta_info.get("title") or meta_info.get("preview") or "") if meta_info else ""
    file_base = build_file_base(cid, meta_info)

    # 1. Guardar Raw JSON
    raw_path = save_raw_json(traj_data, cid)
    print(f"  [1/3] Raw JSON: {os.path.basename(raw_path)}")

    # 2. Guardar Clean JSON
    clean_data = build_clean_conversation(cid, traj_id, steps, title)
    clean_path = save_clean_json(clean_data, file_base)
    print(f"  [2/3] Clean JSON: {os.path.basename(clean_path)} ({len(clean_data['messages'])} msgs)")

    # 3. Guardar Markdown oficial
    if traj_id:
        try:
            md_content = convert_trajectory_to_markdown(port, token, cid, traj_id)
            md_path = save_markdown(md_content, file_base)
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


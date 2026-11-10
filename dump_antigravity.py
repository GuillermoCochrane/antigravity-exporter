#!/usr/bin/env python3
"""
Antigravity Conversation Exporter (CLI)
Orquestador de extracción para sesiones de Antigravity via ConnectRPC y SQLite.
Genera Raw JSON, Clean JSON y Markdown nativo delegando en los módulos de core/.
"""

import os
import argparse
from core import __version__
from core.discovery import find_active_daemon
from core.database import list_conversations, get_conversations_dict
from core.client import AntigravityClient
from core.exporter import export_conversation, export_all_conversations


def main():
    parser = argparse.ArgumentParser(description="Antigravity Conversation Exporter")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--list", action="store_true", help="Listar todas las conversaciones disponibles")
    parser.add_argument("--id", type=str, help="Exportar una conversacion especifica por ID (o prefijo)")
    parser.add_argument("--all", action="store_true", help="Exportar TODAS las conversaciones")
    args = parser.parse_args()

    if args.list:
        convs = list_conversations()
        print(f"\n{'ID':<38} | {'PASOS':<6} | {'FECHA':<10} | {'TITULO / PREVIEW'}")
        print("-" * 90)
        for cid, title, preview, last_mod, steps, _ in convs:
            name = (title or preview or "").strip()
            date_str = last_mod[:10] if last_mod else "N/A"
            print(f"{cid:<38} | {steps:<6} | {date_str:<10} | {name[:35]}")
        return

    if not (args.id or args.all):
        parser.print_help()
        return

    port, token = find_active_daemon()
    print(f"Conectado a Antigravity Daemon (puerto {port})")

    client = AntigravityClient(port, token)
    meta_dict = get_conversations_dict()

    if args.id:
        matched = [cid for cid in meta_dict if cid.startswith(args.id)]
        if not matched:
            print(f"No se encontro ninguna conversacion con ID {args.id}")
            return
        cid = matched[0]
        print(f"\n---> Procesando conversacion: {cid}")
        try:
            paths = export_conversation(client, cid, meta_dict.get(cid))
            print(f"  [1/3] Raw JSON: {os.path.basename(paths['raw'])}")
            print(f"  [2/3] Clean JSON: {os.path.basename(paths['clean'])}")
            if paths.get("markdown"):
                print(f"  [3/3] Markdown: {os.path.basename(paths['markdown'])}")
        except Exception as e:
            print(f"  [ERROR] No se pudo exportar la conversacion: {e}")
    elif args.all:
        print(f"Exportando {len(meta_dict)} conversaciones...")

        def cli_progress(cid, idx, total, paths, error):
            if error:
                print(f"  [{idx}/{total}] ERROR en {cid[:8]}: {error}")
            else:
                print(f"  [{idx}/{total}] OK: {cid[:8]}")

        results = export_all_conversations(client, meta_dict, on_progress=cli_progress)
        success = sum(1 for r in results.values() if r["status"] == "ok")
        print(f"\n[FINALIZADO] Se exportaron con exito {success}/{len(meta_dict)} conversaciones.")


if __name__ == "__main__":
    main()

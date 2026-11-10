"""
Módulo de interfaz de línea de comandos (CLI) de Antigravity Exporter.
Gestiona el parseo de argumentos, formateo visual en terminal y códigos de salida.
"""

import os
import argparse
from core import __version__
from core.discovery import find_active_daemon
from core.database import list_conversations, get_conversations_dict
from core.client import AntigravityClient
from core.exporter import export_conversation, export_all_conversations


def build_parser() -> argparse.ArgumentParser:
    """Construye y configura el parser de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        prog="dump_antigravity.py",
        description="Antigravity Conversation Exporter",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--list", action="store_true", help="Listar todas las conversaciones disponibles"
    )
    parser.add_argument(
        "--id", type=str, help="Exportar una conversacion especifica por ID (o prefijo)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Exportar TODAS las conversaciones"
    )
    return parser


def print_conversations_table(convs: list[tuple]) -> None:
    """Imprime en terminal la tabla formateada del catálogo de sesiones."""
    print(f"\n{'ID':<38} | {'PASOS':<6} | {'FECHA':<10} | {'TITULO / PREVIEW'}")
    print("-" * 90)
    for cid, title, preview, last_mod, steps, _ in convs:
        name = (title or preview or "").strip()
        date_str = last_mod[:10] if last_mod else "N/A"
        print(f"{cid:<38} | {steps:<6} | {date_str:<10} | {name[:35]}")


def run_cli(args_list: list[str] = None) -> int:
    """
    Punto de entrada ejecutable de la CLI.

    Args:
        args_list (list[str], optional): Lista de argumentos explícita (ej: ['--list']).
                                         Si es None, parsea sys.argv[1:].

    Returns:
        int: Código de salida estándar (0: OK, 1: Error o aborto).
    """
    parser = build_parser()
    args = parser.parse_args(args_list)

    if args.list:
        convs = list_conversations()
        print_conversations_table(convs)
        return 0

    if not (args.id or args.all):
        parser.print_help()
        return 1

    try:
        port, token = find_active_daemon()
        print(f"Conectado a Antigravity Daemon (puerto {port})")
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        return 1

    client = AntigravityClient(port, token)
    meta_dict = get_conversations_dict()

    if args.id:
        matched = [cid for cid in meta_dict if cid.startswith(args.id)]
        if not matched:
            print(f"No se encontro ninguna conversacion con ID {args.id}")
            return 1
        cid = matched[0]
        print(f"\n---> Procesando conversacion: {cid}")
        try:
            paths = export_conversation(client, cid, meta_dict.get(cid))
            print(f"  [1/3] Raw JSON: {os.path.basename(paths['raw'])}")
            print(f"  [2/3] Clean JSON: {os.path.basename(paths['clean'])}")
            if paths.get("markdown"):
                print(f"  [3/3] Markdown: {os.path.basename(paths['markdown'])}")
            return 0
        except Exception as e:
            print(f"  [ERROR] No se pudo exportar la conversacion: {e}")
            return 1

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
        return 0 if success > 0 else 1

    return 0


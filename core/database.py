"""
Módulo de base de datos de Antigravity Exporter.
Gestiona la conexión y consultas a conversation_summaries.db (SQLite).
"""

import os
import sqlite3

DEFAULT_BASE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
DEFAULT_DB_PATH = os.path.join(DEFAULT_BASE_DIR, "conversation_summaries.db")


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Retorna una conexión a la base de datos de resúmenes de conversación.
    """
    target_path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"No se encontro la base de datos en: {target_path}")
    return sqlite3.connect(target_path)


def list_conversations(db_path: str = None) -> list[tuple]:
    """
    Obtiene la lista completa de conversaciones ordenadas por fecha de modificación descendente.

    Args:
        db_path (str, optional): Ruta personalizada a conversation_summaries.db.

    Returns:
        list[tuple]: Lista de tuplas:
                     (conversation_id, title, preview, last_modified_time, step_count, workspace_uris)
                     Retorna [] si no existe el archivo o si ocurre un error.
    """
    target_path = db_path or DEFAULT_DB_PATH
    if not os.path.exists(target_path):
        return []

    try:
        conn = get_connection(target_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_id, title, preview, last_modified_time, step_count, workspace_uris 
            FROM conversation_summaries 
            ORDER BY last_modified_time DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def get_conversations_dict(db_path: str = None) -> dict[str, dict]:
    """
    Retorna un diccionario indexado por conversation_id con sus metadatos:
    {
        "conversation_id": {
            "title": str,
            "preview": str,
            "last_modified_time": str,
            "step_count": int,
            "workspace_uris": str
        }
    }
    """
    rows = list_conversations(db_path)
    return {
        r[0]: {
            "title": r[1],
            "preview": r[2],
            "last_modified_time": r[3],
            "step_count": r[4],
            "workspace_uris": r[5],
        }
        for r in rows
    }


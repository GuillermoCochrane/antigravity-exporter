"""
Módulo de normalización y transformación de Antigravity Exporter.
Funciones puras para procesar la trayectoria cruda del daemon y generar Clean JSON.
"""

from datetime import datetime


def parse_iso_timestamp(ts_str: str) -> int | None:
    """
    Convierte una marca de tiempo ISO 8601 (con o sin microsegundos y sufijo Z)
    en un timestamp Unix entero en segundos (epoch seconds).

    Args:
        ts_str (str): Cadena de fecha (ej: '2026-11-01T14:30:00.123456Z').

    Returns:
        int | None: Timestamp entero en segundos o None si falla o es vacío.
    """
    if not ts_str:
        return None
    try:
        clean = ts_str.split(".")[0].rstrip("Z")
        return int(datetime.fromisoformat(clean).timestamp())
    except Exception:
        return None


def extract_clean_messages(steps: list[dict]) -> list[dict]:
    """
    Filtra los pasos de la trayectoria de Antigravity extrayendo exclusivamente
    la conversación dialéctica (humano y modelo), eliminando tool calls,
    outputs de comandos, pensamientos internos y telemetría de sistema.

    Args:
        steps (list[dict]): Lista de pasos del objeto trajectory devuelto por el daemon.

    Returns:
        list[dict]: Lista de mensajes limpios (id, role, timestamp, text).
    """
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


def build_clean_conversation(cid: str, trajectory_id: str, steps: list[dict], title: str = "") -> dict:
    """
    Construye la estructura completa y normalizada del archivo clean_json
    según la especificación de docs/INTEGRATION.md.

    Args:
        cid (str): UUID de la conversación.
        trajectory_id (str): ID interno de la trayectoria devuelta por el daemon.
        steps (list[dict]): Pasos de la trayectoria.
        title (str, optional): Título descriptivo de la conversación.

    Returns:
        dict: Diccionario normalizado con la estructura canónica.
    """
    clean_msgs = extract_clean_messages(steps)
    return {
        "id": cid,
        "trajectoryId": trajectory_id,
        "title": title,
        "stepCount": len(steps),
        "messageCount": len(clean_msgs),
        "messages": clean_msgs
    }

"""
Módulo de escritura y persistencia de Antigravity Exporter.
Gestiona rutas, sanitización de nombres y almacenamiento en disco en los formatos raw, clean y markdown.
"""

import os
import json
import re

DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
)


def get_output_dirs(base_dir: str = None) -> dict[str, str]:
    """
    Retorna el diccionario de directorios de salida canónicos:
    {
        "base": path,
        "raw": path/raw_json,
        "clean": path/clean_json,
        "markdown": path/markdown
    }
    """
    base = base_dir or DEFAULT_OUTPUT_DIR
    return {
        "base": base,
        "raw": os.path.join(base, "raw_json"),
        "clean": os.path.join(base, "clean_json"),
        "markdown": os.path.join(base, "markdown"),
    }


def ensure_output_dirs(base_dir: str = None) -> dict[str, str]:
    """
    Crea los directorios de salida si no existen y retorna el diccionario de rutas.
    Es idempotente: si ya existen, no genera error.
    """
    dirs = get_output_dirs(base_dir)
    for d in [dirs["raw"], dirs["clean"], dirs["markdown"]]:
        os.makedirs(d, exist_ok=True)
    return dirs


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Elimina caracteres incompatibles con sistemas de archivos (\\/*?:"<>|)
    y convierte espacios en guiones bajos.
    """
    clean = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    clean = clean.replace(" ", "_")
    return clean[:max_length] if clean else "conversacion"


def build_file_base(cid: str, meta_info: dict = None) -> str:
    """
    Construye el nombre base legible canónico: YYYY-MM-DD_slug_cid8.
    Ejemplo: '2026-11-01_conversacion_1e706e7b'
    """
    title = ""
    date_prefix = ""
    if meta_info:
        title = meta_info.get("title") or meta_info.get("preview") or ""
        last_mod = meta_info.get("last_modified_time", "")
        if last_mod:
            date_prefix = last_mod[:10] + "_"

    clean_slug = sanitize_filename(title)
    return f"{date_prefix}{clean_slug}_{cid[:8]}"


def save_raw_json(data: dict, cid: str, base_dir: str = None) -> str:
    """
    Guarda el payload crudo de la trayectoria como raw_json/<cid>.raw.json.

    Returns:
        str: Ruta absoluta del archivo creado.
    """
    dirs = ensure_output_dirs(base_dir)
    raw_path = os.path.join(dirs["raw"], f"{cid}.raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return raw_path


def save_clean_json(data: dict, file_base: str, base_dir: str = None) -> str:
    """
    Guarda la conversación normalizada como clean_json/<file_base>.clean.json.

    Returns:
        str: Ruta absoluta del archivo creado.
    """
    dirs = ensure_output_dirs(base_dir)
    clean_path = os.path.join(dirs["clean"], f"{file_base}.clean.json")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return clean_path


def save_markdown(content: str, file_base: str, base_dir: str = None) -> str:
    """
    Guarda el documento compilado oficial como markdown/<file_base>.md.

    Returns:
        str: Ruta absoluta del archivo creado.
    """
    dirs = ensure_output_dirs(base_dir)
    md_path = os.path.join(dirs["markdown"], f"{file_base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    return md_path


def save_conversation_bundle(
    cid: str,
    raw_data: dict,
    clean_data: dict,
    md_content: str = None,
    meta_info: dict = None,
    file_base: str = None,
    base_dir: str = None,
) -> dict[str, str]:
    """
    Persiste de forma atómica los formatos disponibles para una conversación.

    Returns:
        dict[str, str]: Rutas de los archivos creados {'raw': path, 'clean': path, 'markdown': path | None}
    """
    slug = file_base or build_file_base(cid, meta_info)
    raw_path = save_raw_json(raw_data, cid, base_dir=base_dir)
    clean_path = save_clean_json(clean_data, slug, base_dir=base_dir)
    md_path = None
    if md_content is not None:
        md_path = save_markdown(md_content, slug, base_dir=base_dir)

    return {
        "raw": raw_path,
        "clean": clean_path,
        "markdown": md_path,
    }


"""
Módulo orquestador de exportación de Antigravity (Application Layer / Pipeline).
Coordina la interacción entre el cliente ConnectRPC, la normalización y la persistencia en disco.
"""

from core.client import AntigravityClient
from core.normalizer import build_clean_conversation
from core.writer import build_file_base, save_conversation_bundle
from core.database import get_conversations_dict


def export_conversation(
    client: AntigravityClient,
    cid: str,
    meta_info: dict = None,
    base_dir: str = None
) -> dict[str, str]:
    """
    Orquesta el pipeline completo de exportación para una conversación individual.

    Args:
        client (AntigravityClient): Cliente RPC autenticado con puerto y token.
        cid (str): UUID de la conversación.
        meta_info (dict, optional): Metadatos de la conversación (title, last_modified_time).
        base_dir (str, optional): Directorio base de salida personalizado.

    Returns:
        dict[str, str]: Rutas de los archivos generados:
                        {
                            "raw": path,
                            "clean": path,
                            "markdown": path | None
                        }

    Raises:
        RuntimeError: Si la llamada RPC falla o la conversación no existe.
    """
    traj_data = client.get_trajectory(cid)
    traj = traj_data.get("trajectory", {})
    traj_id = traj.get("trajectoryId")
    steps = traj.get("steps", [])

    title = (meta_info.get("title") or meta_info.get("preview") or "") if meta_info else ""
    file_base = build_file_base(cid, meta_info)

    clean_data = build_clean_conversation(cid, traj_id, steps, title)

    md_content = None
    if traj_id:
        try:
            md_content = client.to_markdown(cid, traj_id)
        except Exception:
            md_content = None

    return save_conversation_bundle(
        cid=cid,
        raw_data=traj_data,
        clean_data=clean_data,
        md_content=md_content,
        meta_info=meta_info,
        file_base=file_base,
        base_dir=base_dir,
    )


def export_all_conversations(
    client: AntigravityClient,
    meta_dict: dict[str, dict] = None,
    base_dir: str = None,
    on_progress: callable = None
) -> dict[str, dict]:
    """
    Exporta en lote todas las conversaciones provistas.

    Args:
        client (AntigravityClient): Cliente RPC autenticado.
        meta_dict (dict[str, dict], optional): Catálogo indexado por CID.
                                               Si es None, se consulta via get_conversations_dict().
        base_dir (str, optional): Directorio base de salida.
        on_progress (callable, optional): Callback invocado tras cada exportación:
                                          on_progress(cid, index, total, result, error)

    Returns:
        dict[str, dict]: Diccionario de resultados indexado por CID:
                         {cid: {"status": "ok", "paths": {...}} | {"status": "error", "error": str}}
    """
    catalog = meta_dict if meta_dict is not None else get_conversations_dict()
    results = {}
    total = len(catalog)

    for index, (cid, meta) in enumerate(catalog.items(), start=1):
        try:
            paths = export_conversation(client, cid, meta_info=meta, base_dir=base_dir)
            results[cid] = {"status": "ok", "paths": paths}
            if on_progress:
                on_progress(cid, index, total, paths, None)
        except Exception as e:
            results[cid] = {"status": "error", "error": str(e)}
            if on_progress:
                on_progress(cid, index, total, None, e)

    return results


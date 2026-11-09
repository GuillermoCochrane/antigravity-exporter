"""
Módulo de descubrimiento de daemons de Antigravity.
Localiza sockets activos y tokens CSRF inspeccionando hub_*.json.
"""

import os
import glob
import json
import urllib.request
import urllib.error

DEFAULT_BASE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
DEFAULT_DAEMON_DIR = os.path.join(DEFAULT_BASE_DIR, "daemon")


def is_daemon_alive(port: int, token: str, timeout: float = 1.0) -> bool:
    """
    Verifica si un daemon de Antigravity responde en localhost mediante HTTP GET.
    Requiere el encabezado de autenticación x-codeium-csrf-token.
    """
    url = f"http://127.0.0.1:{port}"
    req = urllib.request.Request(url, headers={"x-codeium-csrf-token": token})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def find_active_daemon(daemon_dir: str = None) -> tuple[int, str]:
    """
    Busca y valida un daemon activo de Antigravity inspeccionando archivos hub_*.json.

    Args:
        daemon_dir (str, optional): Directorio donde se ubican los archivos hub_*.json.
                                    Si es None, usa ~/.gemini/antigravity/daemon.

    Returns:
        tuple[int, str]: (puerto_http, token_csrf) del primer daemon que responda 200 OK.

    Raises:
        RuntimeError: Si no se encuentra ningún daemon activo.
    """
    target_dir = daemon_dir or DEFAULT_DAEMON_DIR
    files = glob.glob(os.path.join(target_dir, "hub_*.json"))

    for f in sorted(files, key=os.path.getmtime, reverse=True):
        try:
            with open(f, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            port = data.get("httpPort")
            token = data.get("csrfToken")
            if port and token and is_daemon_alive(port, token):
                return port, token
        except Exception:
            continue

    raise RuntimeError(
        "No se encontro ningun daemon activo de Antigravity. "
        "Asegurate de que el IDE o CLI este abierto."
    )


"""
Módulo de cliente ConnectRPC de Antigravity Exporter.
Gestiona el transporte HTTP y llamadas RPC hacia el Language Server (agy.exe).
"""

import json
import urllib.request
import urllib.error


def rpc_call(
    port: int,
    token: str,
    method: str,
    payload: dict,
    timeout: float = 60.0
) -> dict:
    """
    Ejecuta una llamada ConnectRPC sobre HTTP/1.1 contra el Language Server local.

    Args:
        port (int): Puerto HTTP del daemon activo.
        token (str): Token CSRF para autenticar la petición.
        method (str): Nombre del método RPC (ej: 'GetCascadeTrajectory').
        payload (dict): Diccionario con los parámetros del request.
        timeout (float): Tiempo máximo de espera en segundos (default 60s).

    Returns:
        dict: Respuesta JSON decodificada del servidor.

    Raises:
        RuntimeError: Si la petición HTTP falla o el servidor responde con error.
    """
    url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/{method}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-codeium-csrf-token": token,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"RPC {method} fallo ({e.code}): {err}")


def get_cascade_trajectory(
    port: int,
    token: str,
    cascade_id: str,
    timeout: float = 60.0
) -> dict:
    """
    Recupera el objeto de trayectoria completo para una conversación dada.

    Args:
        port (int): Puerto HTTP del daemon activo.
        token (str): Token CSRF del daemon.
        cascade_id (str): ID de la conversación (UUID de cascade).
        timeout (float): Tiempo máximo de espera en segundos.

    Returns:
        dict: Payload crudo devuelto por GetCascadeTrajectory.
    """
    return rpc_call(
        port,
        token,
        "GetCascadeTrajectory",
        {"cascadeId": cascade_id},
        timeout=timeout,
    )


def convert_trajectory_to_markdown(
    port: int,
    token: str,
    conversation_id: str,
    trajectory_id: str,
    timeout: float = 60.0
) -> str:
    """
    Solicita al daemon la conversión de una trayectoria a formato Markdown.

    Args:
        port (int): Puerto HTTP del daemon activo.
        token (str): Token CSRF del daemon.
        conversation_id (str): ID de la conversación.
        trajectory_id (str): ID de la trayectoria interna.
        timeout (float): Tiempo máximo de espera en segundos.

    Returns:
        str: Contenido Markdown compilado (cadena vacía si no se genera).
    """
    res = rpc_call(
        port,
        token,
        "ConvertTrajectoryToMarkdown",
        {
            "conversationId": conversation_id,
            "trajectoryId": trajectory_id,
        },
        timeout=timeout,
    )
    return res.get("markdown", "")


class AntigravityClient:
    """
    Cliente ConnectRPC con estado de conexión persistente (puerto y token).
    Simplifica el consumo repetitivo en exportaciones batch o unitarias.
    """

    def __init__(self, port: int, token: str, timeout: float = 60.0):
        self.port = port
        self.token = token
        self.timeout = timeout

    def call(self, method: str, payload: dict) -> dict:
        """Invoca un método RPC arbitrario."""
        return rpc_call(self.port, self.token, method, payload, timeout=self.timeout)

    def get_trajectory(self, cascade_id: str) -> dict:
        """Obtiene la trayectoria cruda de una conversación."""
        return get_cascade_trajectory(self.port, self.token, cascade_id, timeout=self.timeout)

    def to_markdown(self, conversation_id: str, trajectory_id: str) -> str:
        """Convierte una trayectoria a Markdown nativo."""
        return convert_trajectory_to_markdown(
            self.port,
            self.token,
            conversation_id,
            trajectory_id,
            timeout=self.timeout,
        )


# Implementation Plan: Módulo Client (v1.0.4)

## 1. Objetivo y Alcance

Extraer la lógica de comunicación ConnectRPC sobre HTTP (Capa 3 de la Arquitectura) desde `dump_antigravity.py` hacia un módulo dedicado: **`core/client.py`**.

Este módulo es el responsable exclusivo de interactuar con el socket del Language Server (`agy.exe`):
1. Encapsular la construcción de requests HTTP POST hacia el servicio `exa.language_server_pb.LanguageServerService`.
2. Inyectar automáticamente las cabeceras requeridas (`Content-Type: application/json`, `x-codeium-csrf-token`).
3. Gestionar serialización y deserialización JSON nativa con manejo robusto de errores (`urllib.error.HTTPError` -> `RuntimeError`).
4. Proveer helpers de alto nivel para los dos endpoints consumidos por el sistema:
   - `GetCascadeTrajectory`: Obtiene el árbol crudo de pasos de una conversación.
   - `ConvertTrajectoryToMarkdown`: Compila la trayectoria a Markdown mediante el motor nativo de Antigravity.

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### 1. `rpc_call` (Transporte base)
```python
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
```

### 2. `get_cascade_trajectory`
```python
def get_cascade_trajectory(
    port: int, 
    token: str, 
    cascade_id: str, 
    timeout: float = 60.0
) -> dict:
    """
    Recupera el objeto de trayectoria completo para una conversación dada.
    
    Returns:
        dict: Payload crudo con la estructura {'trajectory': {'trajectoryId': ..., 'steps': [...]}}
    """
```

### 3. `convert_trajectory_to_markdown`
```python
def convert_trajectory_to_markdown(
    port: int, 
    token: str, 
    conversation_id: str, 
    trajectory_id: str, 
    timeout: float = 60.0
) -> str:
    """
    Solicita al daemon la conversión de una trayectoria a formato Markdown.
    
    Returns:
        str: Contenido Markdown generado por Antigravity (string vacío si no se genera).
    """
```

### 4. `AntigravityClient` (Clase Opcional de Alta Ergonomía)
```python
class AntigravityClient:
    """
    Cliente ConnectRPC con estado de conexión (puerto y token).
    Simplifica el consumo repetitivo en bucles de exportación.
    """
    def __init__(self, port: int, token: str, timeout: float = 60.0):
        self.port = port
        self.token = token
        self.timeout = timeout

    def call(self, method: str, payload: dict) -> dict:
        return rpc_call(self.port, self.token, method, payload, self.timeout)

    def get_trajectory(self, cascade_id: str) -> dict:
        return get_cascade_trajectory(self.port, self.token, cascade_id, self.timeout)

    def to_markdown(self, conversation_id: str, trajectory_id: str) -> str:
        return convert_trajectory_to_markdown(self.port, self.token, conversation_id, trajectory_id, self.timeout)
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a eliminar:**
  * Implementación monolítica de `rpc_call` (líneas 35 a 47).
* **Líneas a incorporar:**
  ```python
  from core.client import rpc_call, get_cascade_trajectory, convert_trajectory_to_markdown
  # o alternativamente:
  from core.client import AntigravityClient
  ```
* **Limpieza en `export_conversation`:**
  * Reemplazo de invocaciones directas a strings por llamadas a `get_cascade_trajectory` y `convert_trajectory_to_markdown` (o métodos del cliente).

---

## 4. Archivos a Crear / Modificar

1. **`planification/01-modularizacion/implementation_plan_client.md` (Nuevo):**
   * Este documento de planificación y especificación técnica.
2. **`core/client.py` (Nuevo):**
   * Implementación de la Capa 3: `rpc_call`, helpers de alto nivel y clase `AntigravityClient`.
   * Cero dependencias externas (`json`, `urllib.request`, `urllib.error`).
3. **`dump_antigravity.py` (Modificado):**
   * Delegación completa del transporte ConnectRPC en `core.client`.

---

## 5. Checklist de Verificación Manual

- [x] Importar `core.client` de forma aislada y probar llamada contra el daemon activo.
- [x] Ejecutar `python dump_antigravity.py --id 1e706e7b` y validar la recuperación de trayectoria y compilación a Markdown.
- [x] Verificar que si el daemon no responde o se provee un token inválido, se capture el error adecuadamente.

---

## 6. Tríada de Commits para v1.0.4

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de implementacion para modulo client
   ```
2. **Refactor (Código):**
   ```text
   refactor(client): desacoplar cliente connectrpc a core/client
   ```
3. **Docs (Documentación):**
   ```text
   docs(client): documentar modulo core/client, manual_testing y changelog v1.0.4
   ```
4. **Chore (Versión):**
   ```text
   chore: actualizar version a 1.0.4
   ```


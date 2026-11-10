# Implementation Plan: Módulo Discovery (v1.0.1)

## 1. Objetivo y Alcance

Extraer la lógica de localización y validación del daemon local de Antigravity desde `dump_antigravity.py` hacia un módulo dedicado e independiente: **`core/discovery.py`**.

Este módulo será el responsable exclusivo de:
1. Inspeccionar la carpeta de daemons (`~/.gemini/antigravity/daemon/`).
2. Parsear los archivos `hub_*.json` ordenados por fecha de modificación reciente.
3. Probar mediante una petición HTTP ultrarrápida si el socket responde con `200 OK`.
4. Retornar el puerto activo y el token CSRF válido.

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### Función Principal: `find_active_daemon`
```python
def find_active_daemon(daemon_dir: str = None) -> tuple[int, str]:
    """
    Busca y valida un daemon activo de Antigravity inspeccionando hub_*.json.
    
    Args:
        daemon_dir (str, optional): Ruta personalizada a la carpeta daemon.
                                    Si es None, usa ~/.gemini/antigravity/daemon.
                                    
    Returns:
        tuple[int, str]: Tupla con (puerto_http, token_csrf).
        
    Raises:
        RuntimeError: Si no se encuentra ningun daemon activo respondiendo en HTTP 200.
    """
```

### Función Auxiliar: `is_daemon_alive`
```python
def is_daemon_alive(port: int, token: str, timeout: float = 1.0) -> bool:
    """
    Verifica mediante HTTP GET con header x-codeium-csrf-token si el socket responde 200 OK.
    """
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a extraer:** 
  * Definición de `DAEMON_DIR` (línea 26) pasa a ser la constante por defecto de `core/discovery.py`.
  * Función `find_active_daemon()` (líneas 37 a 52).
* **Líneas a incorporar en `dump_antigravity.py`:**
  ```python
  from core.discovery import find_active_daemon
  ```
* **Actualización de versión:**
  * `__version__ = "1.0.1"` en `dump_antigravity.py` y en `core/__init__.py`.

---

## 4. Archivos a Crear / Modificar

1. **`core/__init__.py` (Nuevo):**
   * Declara el paquete `core`.
   * Expone `__version__ = "1.0.1"`.
2. **`core/discovery.py` (Nuevo):**
   * Implementa `DEFAULT_DAEMON_DIR`, `is_daemon_alive` y `find_active_daemon`.
   * Cero dependencias externas (`glob`, `json`, `os`, `urllib.request`, `urllib.error`).
3. **`dump_antigravity.py` (Modificado):**
   * Elimina la implementación interna de `find_active_daemon`.
   * Importa desde `core.discovery`.
   * Actualiza `__version__` a `1.0.1`.

---

## 5. Checklist de Verificación Manual

- [x] Ejecutar `python dump_antigravity.py --version` y validar que responda `dump_antigravity.py 1.0.1`.
- [x] Ejecutar `python dump_antigravity.py --list` y validar que siga listando sin errores.
- [x] Ejecutar `python dump_antigravity.py --id eacc4ff1` y validar que contacte al daemon vía `core/discovery.py` y realice la exportación exitosa.

---

## 6. Commit y Registro de Cambios

* **Scope:** `refactor(discovery)`
* **Mensaje sugerido:**
  ```text
  refactor(discovery): desacoplar deteccion de daemon a core/discovery
  ```


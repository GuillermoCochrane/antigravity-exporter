# Implementation Plan: Módulo Database (v1.0.2)

## 1. Objetivo y Alcance

Extraer la lógica de conexión y consulta a la base de datos SQLite `conversation_summaries.db` desde `dump_antigravity.py` hacia un módulo dedicado e independiente: **`core/database.py`**.

Este módulo será el responsable exclusivo de:
1. Gestionar la ruta por defecto a la base de datos de Antigravity (`~/.gemini/antigravity/conversation_summaries.db`), eliminando rutas absolutas hardcodeadas para respetar **DRY** y portabilidad de usuario.
2. Establecer conexiones en modo solo lectura (`ro` o estándar segura) sin bloquear el proceso de Antigravity IDE.
3. Consultar y ordenar el catálogo histórico de conversaciones registradas.
4. Proveer helpers de búsqueda y filtrado de metadatos por ID o prefijo.

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### Constante de Ruta por Defecto
```python
DEFAULT_BASE_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
DEFAULT_DB_PATH = os.path.join(DEFAULT_BASE_DIR, "conversation_summaries.db")
```

### Función Principal: `list_conversations`
```python
def list_conversations(db_path: str = None) -> list[tuple]:
    """
    Obtiene la lista completa de conversaciones ordenadas por fecha de modificacion descendente.
    
    Args:
        db_path (str, optional): Ruta personalizada a conversation_summaries.db.
                                Si es None, utiliza DEFAULT_DB_PATH.
                                
    Returns:
        list[tuple]: Lista de tuplas con la estructura:
                     (conversation_id, title, preview, last_modified_time, step_count, workspace_uris)
                     Retorna [] si el archivo no existe o ocurre un error.
    """
```

### Función Auxiliar: `get_conversations_dict`
```python
def get_conversations_dict(db_path: str = None) -> dict[str, dict]:
    """
    Retorna un diccionario indexado por conversation_id con sus metadatos limpios:
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
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a eliminar:**
  * `BASE_DIR = r"C:\Users\cochr\.gemini\antigravity"` (línea 23).
  * `SUMMARIES_DB = os.path.join(BASE_DIR, "conversation_summaries.db")` (línea 24).
  * Implementación monolítica de `list_conversations()` (líneas 54 a 67).
* **Líneas a incorporar:**
  ```python
  from core.database import list_conversations
  ```

---

## 4. Archivos a Crear / Modificar

1. **`core/database.py` (Nuevo):**
   * Implementa `DEFAULT_DB_PATH`, `list_conversations()` y `get_conversations_dict()`.
   * Cero dependencias externas (`sqlite3`, `os`).
2. **`dump_antigravity.py` (Modificado):**
   * Elimina la conexión SQLite embebida y la ruta hardcodeada.
   * Importa desde `core.database`.

---

## 5. Checklist de Verificación Manual

- [ ] Ejecutar `python dump_antigravity.py --list` y verificar que liste con éxito las 30 conversaciones.
- [ ] Ejecutar `python dump_antigravity.py --id 1e706e7b` y validar que el lookup de metadatos en SQLite funcione correctamente.
- [ ] Validar que `core/database.py` se pueda importar de forma aislada en una sesión de Python sin depender de otros módulos.

---

## 6. Tríada de Commits para v1.0.2

1. **Refactor (Código):**
   ```text
   refactor(database): desacoplar consultas sqlite a core/database
   ```
2. **Docs (Documentación):**
   * Actualizar `docs/ARCHITECTURE.md` con `core/database.py`.
   * Añadir entrada `v1.0.2` en `docs/CHANGELOG.md`.
   * Marcar Paso 2 como `[x]` en `planification/01-modularizacion/walkthrough.md`.
   * Marcar checklist en este archivo.
   ```text
   docs(database): documentar modulo core/database y changelog para v1.0.2
   ```
3. **Chore (Versión):**
   * Actualizar `__version__ = "1.0.2"` en `core/__init__.py`.
   ```text
   chore: actualizar version a 1.0.2
   ```


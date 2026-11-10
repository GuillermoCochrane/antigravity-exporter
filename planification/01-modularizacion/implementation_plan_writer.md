# Implementation Plan: Módulo Writer (v1.0.5)

## 1. Objetivo y Alcance

Extraer la lógica de persistencia, generación de rutas y sanitización del sistema de archivos (Capa 5 de la Arquitectura: Capa de Salida) desde `dump_antigravity.py` hacia un módulo dedicado: **`core/writer.py`**.

Este módulo es el responsable exclusivo de la interacción con el disco para almacenar las exportaciones:
1. Crear y asegurar la existencia de los directorios de salida (`raw_json`, `clean_json`, `markdown`).
2. Sanitizar caracteres no permitidos en nombres de archivo para compatibilidad cross-platform (Windows y Unix).
3. Formatear el prefijo cronológico y el slug identificador a partir de metadatos (`last_modified_time`, `title` y `cid[:8]`).
4. Persistir con codificación explícita `utf-8` los tres formatos de exportación (`.raw.json`, `.clean.json`, `.md`).
5. Permitir la inyección de un directorio base de salida personalizado (facilitando pruebas con fixtures o carpetas temporales).

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### 1. Constantes y Directorios
```python
# Directorio raíz del proyecto (calculado dinámicamente)
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

def get_output_dirs(base_dir: str = None) -> dict[str, str]:
    """
    Retorna las rutas canónicas para los tres almacenes de salida:
    {
        "base": path,
        "raw": path/raw_json,
        "clean": path/clean_json,
        "markdown": path/markdown
    }
    """

def ensure_output_dirs(base_dir: str = None) -> dict[str, str]:
    """Crea los directorios de salida si no existen y retorna el diccionario de rutas."""
```

### 2. `sanitize_filename` y `build_file_base`
```python
def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Elimina caracteres reservados por sistemas de archivos (\\/*?:"<>|) y normaliza espacios a guiones bajos.
    """

def build_file_base(cid: str, meta_info: dict = None) -> str:
    """
    Construye el nombre base canónico del archivo: YYYY-MM-DD_slug_cid8.
    Ejemplo: '2026-11-01_conversacion_1e706e7b'
    """
```

### 3. Funciones de Persistencia Específica
```python
def save_raw_json(data: dict, cid: str, base_dir: str = None) -> str:
    """Guarda data como raw_json/<cid>.raw.json y retorna la ruta del archivo creado."""

def save_clean_json(data: dict, file_base: str, base_dir: str = None) -> str:
    """Guarda data como clean_json/<file_base>.clean.json y retorna la ruta del archivo creado."""

def save_markdown(content: str, file_base: str, base_dir: str = None) -> str:
    """Guarda content como markdown/<file_base>.md y retorna la ruta del archivo creado."""
```

### 4. Helper Coordinador: `save_conversation_bundle`
```python
def save_conversation_bundle(
    cid: str,
    raw_data: dict,
    clean_data: dict,
    md_content: str = None,
    meta_info: dict = None,
    base_dir: str = None
) -> dict[str, str]:
    """
    Persiste de forma atómica los formatos disponibles para una conversación.
    
    Returns:
        dict[str, str]: Rutas de los archivos creados {'raw': path, 'clean': path, 'markdown': path | None}
    """
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a eliminar:**
  * Constantes de rutas (`ADAPTER_DIR`, `OUTPUT_RAW`, `OUTPUT_CLEAN`, `OUTPUT_MD`).
  * Función `ensure_dirs()`.
  * Función `sanitize_filename()`.
  * Lógica manual de apertura y escritura `open(...)` en `export_conversation`.
* **Líneas a incorporar:**
  ```python
  from core.writer import save_conversation_bundle
  ```
  O sus funciones atómicas:
  ```python
  from core.writer import ensure_output_dirs, build_file_base, save_raw_json, save_clean_json, save_markdown
  ```

---

## 4. Archivos a Crear / Modificar

1. **`planification/01-modularizacion/implementation_plan_writer.md` (Nuevo):**
   * Este documento de planificación y especificación técnica.
2. **`core/writer.py` (Nuevo):**
   * Implementación de la Capa 5: gestión de directorios, nombres seguros y escritura en disco.
   * Cero dependencias externas (`os`, `json`, `re`).
3. **`dump_antigravity.py` (Modificado):**
   * Delegación de toda la persistencia en `core.writer`.

---

## 5. Checklist de Verificación Manual

- [x] Importar `core.writer` de forma aislada y probar generación de nombres y guardado con un directorio temporal.
- [x] Ejecutar `python dump_antigravity.py --id 1e706e7b` y validar que los 3 archivos se sigan generando con exactamente los mismos nombres y contenidos.
- [x] Validar que `ensure_output_dirs` sea idempotente (funcione sin error tanto si las carpetas ya existen como si no).

---

## 6. Tríada de Commits para v1.0.5

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de implementacion para modulo writer
   ```
2. **Refactor (Código):**
   ```text
   refactor(writer): desacoplar persistencia a core/writer
   ```
3. **Docs (Documentación):**
   ```text
   docs(writer): documentar modulo core/writer, manual_testing y changelog v1.0.5
   ```
4. **Chore (Versión):**
   ```text
   chore: actualizar version a 1.0.5
   ```


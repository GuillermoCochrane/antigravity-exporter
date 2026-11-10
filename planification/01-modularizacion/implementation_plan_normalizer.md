# Implementation Plan: Módulo Normalizer (v1.0.3)

## 1. Objetivo y Alcance

Extraer la lógica de transformación y limpieza de datos (Capa 4 de la Arquitectura) desde `dump_antigravity.py` hacia un módulo dedicado: **`core/normalizer.py`**.

Este módulo es **la pieza central de la pureza arquitectónica del sistema**:
1. No realiza llamadas de red ni lecturas de base de datos.
2. No interactúa con el sistema de archivos (cero I/O).
3. Recibe estructuras de datos en memoria (diccionarios y listas) y devuelve estructuras normalizadas y validadas.
4. Al ser **100% funciones puras**, habilita el desarrollo inmediato de tests unitarios con fixtures en la Fase 3 (`v1.2.0`).

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### 1. `parse_iso_timestamp`
```python
def parse_iso_timestamp(ts_str: str) -> int | None:
    """
    Convierte una marca de tiempo ISO 8601 (con o sin microsegundos y sufijo Z)
    en un timestamp Unix entero en segundos (epoch seconds).
    
    Args:
        ts_str (str): Cadena de fecha (ej: '2026-11-01T14:30:00.123456Z').
        
    Returns:
        int | None: Timestamp entero en segundos o None si falla o es vacio.
    """
```

### 2. `extract_clean_messages`
```python
def extract_clean_messages(steps: list[dict]) -> list[dict]:
    """
    Filtra los pasos de la trayectoria de Antigravity extrayendo exclusivamente
    la conversacion dialectica (humano y modelo), eliminando tool calls,
    outputs de comandos, pensamientos internos y telemetria de sistema.
    
    Args:
        steps (list[dict]): Lista de pasos del objeto trajectory devuelto por el daemon.
        
    Returns:
        list[dict]: Lista de mensajes limpios con la estructura:
                    [
                        {
                            "id": str,
                            "role": "user" | "assistant",
                            "timestamp": int | None,
                            "text": str
                        },
                        ...
                    ]
    """
```

### 3. `build_clean_conversation` (Helper de Alto Nivel)
```python
def build_clean_conversation(cid: str, steps: list[dict], meta_info: dict = None) -> dict:
    """
    Construye la estructura completa y normalizada del archivo clean_json
    segun la especificacion de docs/INTEGRATION.md.
    
    Returns:
        dict: {
            "id": str,
            "title": str,
            "last_modified": str | None,
            "step_count": int,
            "messages": list[dict]
        }
    """
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a eliminar:**
  * `parse_iso_timestamp(ts_str)` (líneas 53 a 61).
  * `extract_clean_messages(steps)` (líneas 62 a 95).
* **Líneas a incorporar:**
  ```python
  from core.normalizer import extract_clean_messages, build_clean_conversation
  ```

---

## 4. Archivos a Crear / Modificar

1. **`core/normalizer.py` (Nuevo):**
   * Implementa `parse_iso_timestamp`, `extract_clean_messages` y `build_clean_conversation`.
   * Cero dependencias externas (`datetime`, `re`).
2. **`dump_antigravity.py` (Modificado):**
   * Elimina las funciones de normalización embebidas.
   * Importa desde `core.normalizer`.

---

## 5. Checklist de Verificación Manual

- [ ] Probar `parse_iso_timestamp` con timestamps ISO reales (`2026-11-01T14:30:00Z` y microsegundos).
- [ ] Probar `extract_clean_messages` pasando un mock con pasos de sistema, tool calls y turnos dialécticos.
- [ ] Ejecutar `python dump_antigravity.py --id 1e706e7b` y validar que el archivo `clean_json` generado sea exactamente igual al previo.

---

## 6. Tríada de Commits para v1.0.3

1. **Refactor (Código):**
   ```text
   refactor(normalizer): desacoplar transformacion pura a core/normalizer
   ```
2. **Docs (Documentación):**
   * Actualizar `docs/ARCHITECTURE.md` con `core/normalizer.py`.
   * Añadir casos de prueba en `docs/MANUAL_TESTING.md`.
   * Añadir entrada `v1.0.3` en `docs/CHANGELOG.md`.
   * Marcar Paso 3 como `[x]` en `walkthrough.md`.
   * Marcar checklist en este plan.
   ```text
   docs(normalizer): documentar modulo core/normalizer, manual_testing y changelog v1.0.3
   ```
3. **Chore (Versión):**
   * Actualizar `__version__ = "1.0.3"` en `core/__init__.py`.
   ```text
   chore: actualizar version a 1.0.3
   ```


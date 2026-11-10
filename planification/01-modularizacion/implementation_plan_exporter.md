# Implementation Plan: Módulo Exporter (v1.0.6)

## 1. Objetivo y Alcance

Extraer la orquestación del flujo de exportación (Application Layer / Caso de Uso) desde `dump_antigravity.py` hacia un módulo dedicado: **`core/exporter.py`**.

Este módulo actúa como el **handler o motor de exportación headless**:
1. Recibe un cliente ConnectRPC (`AntigravityClient`), el identificador de la conversación (`cid`) y los metadatos descriptivos.
2. Recupera la trayectoria cruda consumiendo `core.client`.
3. Normaliza y extrae los turnos dialécticos consumiendo `core.normalizer`.
4. Compila el documento Markdown nativo consumiendo `core.client`.
5. Persiste el conjunto de artefactos (`raw_json`, `clean_json`, `markdown`) consumiendo `core.writer`.
6. Opera de forma completamente desacoplada de la interfaz de consola (`print` o `argparse`), permitiendo soportar callbacks de progreso opcionales para CLI, interfaces gráficas o tests automatizados.

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### 1. `export_conversation` (Unitario)
```python
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
```

### 2. `export_all_conversations` (Batch)
```python
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
                                               Si es None, lo consulta via core.database.
        base_dir (str, optional): Directorio base de salida.
        on_progress (callable, optional): Callback invocado tras cada exportación:
                                          on_progress(cid, index, total, result, error=None)
                                          
    Returns:
        dict[str, dict]: Diccionario de resultados indexado por CID con rutas o errores.
    """
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Líneas a eliminar:**
  * Implementación embebida de `export_conversation(...)`.
* **Líneas a incorporar:**
  ```python
  from core.exporter import export_conversation, export_all_conversations
  ```
* **Comportamiento en CLI:**
  * El CLI delega la exportación individual y masiva en `core.exporter`.
  * La presentación en terminal (mensajes `[1/3] Raw JSON`, tablas y feedback visual) puede realizarse mediante un simple callback de consola o formateador visual.

---

## 4. Archivos a Crear / Modificar

1. **`planification/01-modularizacion/implementation_plan_exporter.md` (Nuevo):**
   * Especificación técnica del módulo exporter.
2. **`core/exporter.py` (Nuevo):**
   * Implementación de la orquestación headless del flujo de datos.
   * Conecta `core.client`, `core.normalizer` y `core.writer`.
3. **`dump_antigravity.py` (Modificado):**
   * Consume `core.exporter` eliminando la lógica de pipeline del entrypoint.

---

## 5. Checklist de Verificación Manual

- [x] Importar `core.exporter` de forma aislada y validar que exponga `export_conversation` y `export_all_conversations`.
- [x] Ejecutar prueba programática en Python llamando `export_conversation` y verificar que retorne el diccionario de rutas generado.
- [x] Ejecutar `python dump_antigravity.py --id 1e706e7b` y validar que el CLI coordine con `core.exporter` y conserve el comportamiento idéntico.

---

## 6. Tríada de Commits para v1.0.6

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de implementacion para modulo exporter
   ```
2. **Refactor (Código):**
   ```text
   refactor(exporter): desacoplar orquestacion del motor a core/exporter
   ```
3. **Docs (Documentación):**
   ```text
   docs(exporter): documentar modulo core/exporter, manual_testing y changelog v1.0.6
   ```
4. **Chore (Versión):**
   ```text
   chore: actualizar version a 1.0.6
   ```


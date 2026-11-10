# Changelog

Este documento registra la evolución del proyecto versión por versión y resume las principales decisiones técnicas y capacidades incorporadas en cada entrega.

---

# v1.0.6 — Desacoplamiento del módulo exporter

* **Modularización de la Capa de Aplicación (Motor Headless):**
  * Se crea `core/exporter.py` aislando la orquestación del pipeline de exportación del script CLI.
  * Se implementa `export_conversation` para coordinar de forma headless la llamada RPC, la normalización dialéctica y el almacenamiento multi-formato.
  * Se implementa `export_all_conversations` para procesamiento por lotes con soporte de callbacks de progreso desacoplados de la terminal.
  * `dump_antigravity.py` delega el flujo de exportación en `core.exporter`, reduciendo su responsabilidad exclusivamente a la interacción visual con el usuario.

* **Testing y Evidencia:**
  * Se incorpora la suite de pruebas para `core/exporter.py` en `docs/MANUAL_TESTING.md`.
  * Se valida la importación aislada, la invocación programática pura (modo biblioteca / SDK) y la exportación completa vía CLI con `--id`.

* **Arquitectura y Tracking:**
  * Se actualiza `docs/ARCHITECTURE.md` incorporando `core/exporter.py` en la estructura del proyecto y en el detalle de la Capa 6.
  * Se completa el Paso 6 en `planification/01-modularizacion/walkthrough.md` y en `implementation_plan_exporter.md`.

---

# v1.0.5 — Desacoplamiento del módulo writer

* **Modularización de la Capa de Salida y Persistencia:**
  * Se crea `core/writer.py` centralizando la gestión de rutas del sistema de archivos y almacenamiento en disco.
  * Se implementa `ensure_output_dirs` para la inicialización idempotente de las carpetas de salida (`raw_json`, `clean_json`, `markdown`).
  * Se extraen `sanitize_filename` y `build_file_base` para la generación de nombres seguros y cross-platform.
  * Se implementan las funciones atómicas `save_raw_json`, `save_clean_json` y `save_markdown` con codificación explícita `utf-8`.
  * Se incorpora `save_conversation_bundle` para la persistencia unificada de todos los formatos disponibles.
  * `dump_antigravity.py` delega toda la persistencia en `core.writer`, reduciendo su tamaño a 105 líneas y eliminando dependencias de `json`, `re` y `datetime`.

* **Testing y Evidencia:**
  * Se incorpora la suite de pruebas para `core/writer.py` en `docs/MANUAL_TESTING.md`.
  * Se valida la sanitización de nombres, creación de directorios y la persistencia end-to-end con `--id`.

* **Arquitectura y Tracking:**
  * Se actualiza `docs/ARCHITECTURE.md` incorporando `core/writer.py` en la estructura del proyecto y en el detalle de la Capa 5.
  * Se completa el Paso 5 en `planification/01-modularizacion/walkthrough.md` y en `implementation_plan_writer.md`.

---

# v1.0.4 — Desacoplamiento del módulo client

* **Modularización de la Capa de Comunicación (ConnectRPC):**
  * Se crea `core/client.py` encapsulando todo el transporte HTTP y las llamadas ConnectRPC hacia el Language Server de Antigravity (`agy.exe`).
  * Se implementa `rpc_call` con inyección obligatoria de cabeceras (`Content-Type: application/json` y `x-codeium-csrf-token`) y gestión de errores `urllib.error.HTTPError`.
  * Se extraen los helpers de alto nivel `get_cascade_trajectory` y `convert_trajectory_to_markdown`.
  * Se introduce la clase `AntigravityClient` para mantener estado de conexión (`port`, `token`) y simplificar la exportación por lotes.
  * `dump_antigravity.py` delega las llamadas RPC en `core.client` eliminando dependencias de `urllib` en el orquestador.

* **Testing y Evidencia:**
  * Se incorpora la suite de pruebas para `core/client.py` en `docs/MANUAL_TESTING.md`.
  * Se valida la importación aislada, la invocación mediante `AntigravityClient` y la exportación completa end-to-end con `--id`.

* **Arquitectura y Tracking:**
  * Se actualiza `docs/ARCHITECTURE.md` incorporando `core/client.py` en la estructura del proyecto y en el detalle de la Capa 3.
  * Se completa el Paso 4 en `planification/01-modularizacion/walkthrough.md` y en `implementation_plan_client.md`.

---

# v1.0.3 — Desacoplamiento del módulo normalizer

* **Modularización de la Capa de Transformación y Normalización:**
  * Se crea `core/normalizer.py` aislando las funciones de parseo y transformación pura.
  * Se implementa `parse_iso_timestamp` para convertir marcas ISO 8601 a timestamps Unix enteros.
  * Se implementa `extract_clean_messages` para aislar turnos dialécticos (`user` y `assistant`) filtrando llamadas a herramientas, ejecuciones de terminal y pensamientos.
  * Se implementa `build_clean_conversation` como helper de alto nivel para generar el esquema normalizado de `clean_json`.
  * `dump_antigravity.py` delega la normalización en `core.normalizer` sin efectos secundarios (100% funciones puras, cero I/O).

* **Testing y Evidencia:**
  * Se incorpora la suite de pruebas manuales para `core/normalizer.py` en `docs/MANUAL_TESTING.md`.
  * Se valida la transformación de marcas de tiempo y el filtrado de turnos en memoria, y la exportación end-to-end con `--id`.

* **Arquitectura y Tracking:**
  * Se actualiza `docs/ARCHITECTURE.md` reflejando `core/normalizer.py` en el árbol y en la descripción de la Capa 4.
  * Se completa el Paso 3 en `planification/01-modularizacion/walkthrough.md` y en `implementation_plan_normalizer.md`.

---

# v1.0.2 — Desacoplamiento del módulo de base de datos y catálogo

* **Modularización de la Capa de Catálogo:**
  * Se crea `core/database.py` aislando las consultas a `conversation_summaries.db`.
  * Se eliminan rutas hardcodeadas de usuario en `dump_antigravity.py`, centralizando `DEFAULT_DB_PATH` con `os.path.expanduser("~")` respetando DRY.
  * Se implementan `list_conversations` y el helper indexado `get_conversations_dict`.
  * `dump_antigravity.py` delega las consultas SQLite en `core.database`.

* **Testing y Evidencia:**
  * Se incorpora `docs/MANUAL_TESTING.md` para asentar casos de prueba manuales y resultados observables por versión.
  * Se documenta la prueba de importación aislada, listado de catálogo y lookup de metadatos.

* **Arquitectura y Tracking:**
  * Se actualiza `docs/ARCHITECTURE.md` reflejando la extracción del módulo.
  * Se completa el Paso 2 en el tracker de `planification/01-modularizacion/walkthrough.md`.

---

# v1.0.1 — Desacoplamiento del módulo de descubrimiento de daemons

* **Modularización de la Capa de Descubrimiento:**
  * Se crea el paquete `core/` y el módulo `core/discovery.py`.
  * Se extraen las funciones `find_active_daemon` e `is_daemon_alive`, independizándolas del script monolítico.
  * Se añade soporte para inyección de rutas de daemons personalizadas (`daemon_dir`).
  * `dump_antigravity.py` delega la detección en `core.discovery`, manteniendo la retrocompatibilidad total del CLI.

* **Planificación y Tracking:**
  * Se inaugura el Sprint 01 en `planification/01-modularizacion/` con `walkthrough.md` e `implementation_plan_discovery.md`.

---

# v1.0.0 — Extractor local y adaptador ConnectRPC de Antigravity

* **Ingeniería Inversa y Telemetría:**
  * Se descubre el mecanismo de comunicación del daemon de Antigravity (`agy.exe`) basado en ConnectRPC sobre HTTP local.
  * Se implementa la detección automática de puertos activos y tokens CSRF inspeccionando `~/.gemini/antigravity/daemon/hub_*.json`.
  * Se catalogan 40 sondas experimentales en `lab/` cubriendo encoding, análisis de entropía de archivos `.pb`, inspección de bases SQLite y llamadas RPC.
  * Se documenta la bitácora científica de hipótesis y experimentos en `docs/LABORATORY.md`.

* **Motor de Extracción CLI (`dump_antigravity.py`):**
  * Se desarrolla una CLI autocontenida sin dependencias externas basada en la biblioteca estándar de Python (`urllib.request`, `sqlite3`, `json`, `argparse`).
  * Se añade soporte para listado interactivo de sesiones (`--list`) consultando `conversation_summaries.db`.
  * Se implementa extracción selectiva por ID o prefijo de conversación (`--id <UUID>`).
  * Se añade extracción masiva en lote (`--all`) para exportar todo el catálogo de conversaciones locales.

* **Pipeline de Triple Salida:**
  * Se crea `output/raw_json/`: Respaldo del payload íntegro devuelto por `GetCascadeTrajectory` sin pérdida de telemetría.
  * Se crea `output/clean_json/`: Generación de un esquema normalizado de mensajes (id, rol, texto, timestamp) para consumo de herramientas externas.
  * Se crea `output/markdown/`: Obtención del Markdown oficial generado por el propio daemon mediante `ConvertTrajectoryToMarkdown`.

* **Integración y Compatibilidad:**
  * Se define y valida el contrato de integración con `chat-exporter` mediante el adapter `antigravityParser.js`.
  * Se verifica la compatibilidad de extremo a extremo con el pipeline `filter` ➡️ `normalizer` ➡️ `markdown`.

* **Documentación y Arquitectura:**
  * Se formaliza la arquitectura en 6 capas operativas en `docs/ARCHITECTURE.md`.
  * Se registran las decisiones de diseño ADR-0001 a ADR-0005 en `docs/DECISIONS.md`.
  * Se documenta el flujo de datos en `docs/DATA_FLOW.md` y el contrato de interfaces en `docs/INTEGRATION.md`.
  * Se define el mapa de evolución técnica en `docs/ROADMAP.md`.


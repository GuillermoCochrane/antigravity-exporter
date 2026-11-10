# Changelog

Este documento registra la evolución del proyecto versión por versión y resume las principales decisiones técnicas y capacidades incorporadas en cada entrega.

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


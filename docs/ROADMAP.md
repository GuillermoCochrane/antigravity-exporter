# Roadmap

Este documento define la evolución técnica y las etapas de desarrollo planificadas para **Antigravity Exporter**.

---

## Estado Actual

### v1.0.0 — Hito Fundacional (Completado)

* [x] **Ingeniería Inversa:** Descubrimiento del daemon local Go (`agy.exe`) y su comunicación sobre ConnectRPC / HTTP.
* [x] **Detección Dinámica:** Localización de sockets activos y lectura de tokens CSRF desde `~/.gemini/antigravity/daemon/hub_*.json`.
* [x] **Motor CLI:** Implementación de `dump_antigravity.py` con la librería estándar de Python (cero dependencias externas).
* [x] **Operación:** Soporte para listado interactivo (`--list`), extracción individual (`--id`) y lote completo (`--all`).
* [x] **Triple Pipeline de Salida:**
  * `raw_json`: Captura íntegra del árbol de telemetría y ejecución.
  * `clean_json`: Contrato normalizado de mensajes (User/Model) para exportadores externos.
  * `markdown`: Renderizado oficial del propio motor de Antigravity.
* [x] **Laboratorio de Investigación:** 40 sondas catalogadas en `lab/` y bitácora experimental en `LABORATORY.md`.
* [x] **Integración Validada:** Contrato verificado con `chat-exporter` mediante `antigravityParser.js`.
* [x] **Suite Documental:** Especificaciones completas en `ARCHITECTURE.md`, `DATA_FLOW.md`, `DECISIONS.md` e `INTEGRATION.md`.

---

## Próximos Hitos

### Fase 2: Modularización y Desacoplamiento (v1.1.0)

* **Objetivo:** Transformar el script monolítico `dump_antigravity.py` en una arquitectura modular por capas con responsabilidades delimitadas.
* **Módulos proyectados:**
  * `core/discovery.py`: Detección de daemon activo, lectura de tokens y validación de sockets.
  * `core/database.py`: Consultas de metadatos sobre `conversation_summaries.db` (SQLite).
  * `core/client.py`: Transporte HTTP ConnectRPC (`GetCascadeTrajectory` y `ConvertTrajectoryToMarkdown`).
  * `core/normalizer.py`: Funciones puras de transformación desde payload de daemon a `clean_json`.
  * `core/writer.py`: Gestión del sistema de archivos y persistencia de las 3 salidas.
  * `cli.py`: Orquestador de entrada y manejo de argumentos con `argparse`.
* **Criterio:** Mantener cero dependencias externas y compatibilidad total con la interfaz de comandos actual.

---

### Fase 3: Batería de Pruebas Automatizadas y Fixtures (v1.2.0)

* **Objetivo:** Blindar el conocimiento del sistema frente a cambios de versión o updates del daemon de Antigravity.
* **Alcance:**
  * Implementar suite de tests declarativos (`test/cases/` + `test/runner.py`) usando `unittest` nativo de Python.
  * Incorporar fixtures anonimizados de `trajectory.json` para testear el `normalizer` como función pura.
  * Tests de integración para `database.py` utilizando bases de datos SQLite en memoria (`:memory:`).
  * Tests de verificación de salida en disco sobre directorios temporales aislados.

---

### Fase 4: Empaquetado como Antigravity Custom Skill (v1.3.0)

* **Objetivo:** Habilitar al propio agente de Antigravity para autoinvocar la extracción o consultar su memoria histórica.
* **Alcance:**
  * Crear el descriptor oficial `SKILL.md` bajo `~/.gemini/antigravity/skills/antigravity-exporter/`.
  * Habilitar introspección: el agente podrá recuperar contexto y decisiones técnicas de sesiones anteriores para resolver problemas sin amnesia contextual.

---

### Fase 5: Búsqueda Avanzada y Filtrado (v1.4.0)

* **Objetivo:** Optimizar la recuperación de información específica sin volcar historiales completos.
* **Alcance:**
  * Flag `--query "texto"`: Búsqueda全文 (FTS5) sobre el índice de conversaciones de `conversation_summaries.db`.
  * Flags temporales: `--since YYYY-MM-DD` y `--until YYYY-MM-DD` para acotar rangos de trabajo.
  * Filtro por rol en la salida: opción para exportar exclusivamente prompts de usuario o respuestas del modelo.

---

### Fase 6: Integración con Extensión `chat-exporter` (v2.0.0)

* **Objetivo:** Unificar la experiencia de usuario y permitir descargas locales directamente desde el navegador.
* **Alcance:**
  * Crear un puente local liviano (Chrome Native Messaging Host o micro-servidor local en `127.0.0.1`).
  * Integrar en el popup de la extensión `chat-exporter` la opción "Antigravity Local" para exportar con un solo clic.


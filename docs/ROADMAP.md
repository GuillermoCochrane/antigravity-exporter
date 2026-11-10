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

### v1.1.0 — Modularización y Arquitectura Hexagonal (Completado)

* [x] **Arquitectura en Capas:** Desacoplamiento total del script monolítico original en el paquete `core/`.
* [x] **Capa 2 (Discovery):** `core/discovery.py` con localización dinámica de descriptores `hub_*.json` y chequeo de socket vivo.
* [x] **Capa 1 (Database):** `core/database.py` con consultas SQLite aisladas y helpers de metadatos (`list_conversations`, `get_conversations_dict`).
* [x] **Capa 3 (Client):** `core/client.py` con transporte ConnectRPC sobre HTTP, inyección de tokens y clase `AntigravityClient`.
* [x] **Capa 4 (Normalizer):** `core/normalizer.py` con funciones 100% puras (cero I/O) para filtrar turnos dialécticos y timestamps.
* [x] **Capa 5 (Writer):** `core/writer.py` con creación idempotente de carpetas, sanitización cross-platform y persistencia en `utf-8`.
* [x] **Capa 6 (Exporter):** `core/exporter.py` con orquestación headless del pipeline para consumo como SDK o por lotes.
* [x] **Capa de Presentación (CLI):** `core/cli.py` con configuración de `argparse`, renderizado de tablas y soporte para tests en memoria.
* [x] **Runner Ejecutable:** `dump_antigravity.py` reducido a un launcher mínimo de 11 líneas.
* [x] **Batería de Regresión:** Verificación exitosa de los 4 modos del CLI (`--version`, `--help`, `--list`, `--id`).
* [x] **Metodología y Convención:** Incorporación de plantillas estándar de commits en `planification/rules/COMMIT_TEMPLATES.md`.

---

## Próximos Hitos

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


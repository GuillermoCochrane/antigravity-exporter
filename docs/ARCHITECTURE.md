# Arquitectura

## Índice

- [Filosofía](#filosofía)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Diagrama de Arquitectura](#diagrama-de-arquitectura)
- [Capas del Sistema](#capas-del-sistema)
  - [1. Capa de Catálogo y Metadatos (SQLite)](#1-capa-de-catálogo-y-metadatos-sqlite)
  - [2. Capa de Descubrimiento de Socket (Daemon Hub)](#2-capa-de-descubrimiento-de-socket-daemon-hub)
  - [3. Capa de Comunicación (ConnectRPC Client)](#3-capa-de-comunicación-connectrpc-client)
  - [4. Capa de Transformación y Normalización](#4-capa-de-transformación-y-normalización)
  - [5. Capa de Salida (Multi-formato y Persistencia)](#5-capa-de-salida-multi-formato-y-persistencia)
  - [6. Capa de Aplicación y Orquestación (Export Engine)](#6-capa-de-aplicación-y-orquestación-export-engine)
  - [7. Capa de Integración Externa (Adapter)](#7-capa-de-integración-externa-adapter)
- [Módulos y Responsabilidades](#módulos-y-responsabilidades)
  - [CLI de Producción (`dump_antigravity.py`)](#cli-de-producción-dump_antigravitypy)
  - [Laboratorio de Investigación (`lab/`)](#laboratorio-de-investigación-lab)
  - [Documentación y Memoria (`docs/` y `planification/`)](#documentación-y-memoria-docs-y-planification)
- [Principios de Diseño](#principios-de-diseño)

---

## Filosofía

El proyecto se rige bajo los principios:

- **KISS (Keep It Simple, Stupid):** Priorizar la comunicación por HTTP nativo sobre ingeniería inversa destructiva de archivos binarios en caliente.
- **DRY (Don't Repeat Yourself):** Reutilizar los propios renderizadores del motor oficial en lugar de reimplementar parsers redundantes.
- **SRP (Single Responsibility Principle):** Cada capa resuelve un único problema (catálogo, transporte, normalización, escritura).
- **Cero dependencias en producción:** Implementado íntegramente en Python 3 utilizando la biblioteca estándar (`urllib.request`, `json`, `sqlite3`, `argparse`, `re`).
- **Respeto a la fuente de la verdad:** Preservación del JSON crudo original para garantizar la inmutabilidad y fidelidad del archivo histórico.

---

## Estructura del Proyecto

```text
antigravity-exporter/
├── dump_antigravity.py         # Runner ejecutable mínimo (invoca core.cli)
├── README.md                   # Documentación general y guía rápida
├── LICENSE                     # Licencia pública MIT
├── .gitignore                  # Reglas de exclusión (aislamiento estricto de output/)
│
├── core/                       # Módulos del sistema (Arquitectura en capas)
│   ├── __init__.py             # Inicializador del paquete core
│   ├── cli.py                  # Adaptador CLI: Intérprete de comandos y presentación de consola
│   ├── client.py               # Capa 3: Cliente ConnectRPC y transporte HTTP
│   ├── database.py             # Capa 1: Catálogo y consultas SQLite
│   ├── discovery.py            # Capa 2: Descubrimiento de socket y validación de daemon
│   ├── exporter.py             # Capa 6: Orquestación del motor de exportación (Pipeline)
│   ├── normalizer.py           # Capa 4: Transformación pura de payload a Clean JSON
│   └── writer.py               # Capa 5: Persistencia segura y gestión de rutas en disco
│
├── docs/                       # Documentación técnica retrospectiva (Estado resultante)
│   ├── ARCHITECTURE.md         # Diseño arquitectónico y módulos
│   ├── CHANGELOG.md            # Registro de evolución histórica y versiones
│   ├── DATA_FLOW.md            # Diagrama del flujo y transformación de datos
│   ├── DECISIONS.md            # Registro de decisiones arquitectónicas (ADRs)
│   ├── INTEGRATION.md          # Especificación del contrato con chat-exporter
│   ├── LABORATORY.md           # Registro de hipótesis, experimentos y descubrimientos
│   ├── MANUAL_TESTING.md       # Casos y evidencias de pruebas manuales por versión
│   └── ROADMAP.md              # Estado actual y próximos hitos planificados
│
├── planification/              # Documentación prospectiva (Planes y directivas por sprint)
│   ├── 00-inicial/             # Bitácora y planificación fundacional (v1.0.0)
│   └── 01-modularizacion/      # Sprint activo: walkthrough e implementation plans
│
├── lab/                        # Sondas de laboratorio y desensamblado
│   ├── README.md               # Catálogo descriptivo de sondas experimentales
│   ├── database/               # Inspección de bases SQLite y tablas FTS5
│   ├── encoding/               # Análisis de compresión y binarios (.pb / agy.exe)
│   ├── rpc_discovery/          # Rastreo de métodos y schemas ConnectRPC en JS
│   └── rpc_tests/              # Sondas dinámicas de invocación contra el daemon
│
└── output/                     # Almacén de artefactos exportados (excluido de git)
    ├── raw_json/               # Volcados íntegros del árbol de la API
    ├── clean_json/             # Diálogos normalizados para entrenamiento o ingesta
    └── markdown/               # Documentos legibles oficiales renderizados
```

---

## Diagrama de Arquitectura

```text
┌────────────────────────────────────────────────────────┐
│                   Antigravity IDE                      │
│                                                        │
│  ┌─────────────────────────┐  ┌─────────────────────┐  │
│  │ conversation_summaries  │  │   agy.exe Daemon    │  │
│  │      (SQLite DB)        │  │     ConnectRPC      │  │
│  └────────────┬────────────┘  └──────────┬──────────┘  │
└───────────────┼──────────────────────────┼─────────────┘
                │                          │
      1. Catálogo / Metadata       2. RPC HTTP Socket
                │                 (:port + csrfToken)
                ▼                          │
┌──────────────────────────────────────────┼─────────────┐
│          dump_antigravity.py             ▼             │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. Hub Discovery: lee daemon/hub_*.json          │  │
│  │ 2. Catálogo: enumera IDs y títulos en SQLite     │  │
│  │ 3. ConnectRPC Client:                            │  │
│  │    • GetCascadeTrajectory (Árbol crudo)          │  │
│  │    • ConvertTrajectoryToMarkdown (Markdown)      │  │
│  │ 4. Normalizer: Extrae turnos User / Assistant    │  │
│  └──────────────────────────┬───────────────────────┘  │
└─────────────────────────────┼──────────────────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      ┌────────────┐   ┌────────────┐   ┌────────────┐
      │  raw_json  │   │ clean_json │   │  markdown  │
      └────────────┘   └──────┬─────┘   └────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │        chat-exporter         │
               │   (antigravityParser.js)     │
               └──────────────────────────────┘
```

---

## Capas del Sistema

### 1. Capa de Catálogo y Metadatos (SQLite)
* **Módulo:** `core/database.py` (`list_conversations` y `get_conversations_dict`)
* **Archivo consultado:** `~/.gemini/antigravity/conversation_summaries.db`
* **Responsabilidad:** Proporcionar la lista exhaustiva de conversaciones históricas (`conversation_id`), fechas de modificación (`last_modified_time`), cantidad de pasos acumulados (`step_count`) y títulos o descripciones preliminares (`title`, `preview`).
* **Comportamiento:** Solo lectura pasiva. No altera los registros ni compite con el bloqueo de base de datos del IDE.

### 2. Capa de Descubrimiento de Socket (Daemon Hub)
* **Módulo:** `core/discovery.py` (`find_active_daemon` e `is_daemon_alive`)
* **Directorio escaneado:** `~/.gemini/antigravity/daemon/hub_*.json`
* **Responsabilidad:** Identificar dinámicamente cuál de los daemons generados por sesiones previas se encuentra activo en el sistema.
* **Mecanismo:** Ordena los descriptores por fecha de modificación descendente y ejecuta un sondeo HTTP no intrusivo con timeout de 1 segundo. El primer descriptor que devuelve estado `200` autenticado provee el puerto activo y el token CSRF para el resto de la sesión.

### 3. Capa de Comunicación (ConnectRPC Client)
* **Módulo:** `core/client.py` (`rpc_call`, `get_cascade_trajectory`, `convert_trajectory_to_markdown`, `AntigravityClient`)
* **Protocolo:** ConnectRPC sobre HTTP/1.1 (especificación estándar de Buf/gRPC).
* **Cabeceras obligatorias:**
  * `Content-Type: application/json`
  * `x-codeium-csrf-token: <CSRF_TOKEN>`
* **Endpoints consumidos:**
  * `POST /exa.language_server_pb.LanguageServerService/GetCascadeTrajectory`: Recupera el árbol con todos los pasos secuenciales de la conversación (`cascadeId`).
  * `POST /exa.language_server_pb.LanguageServerService/ConvertTrajectoryToMarkdown`: Delega en el compilador nativo del Language Server la generación del texto formateado en Markdown.
* **Ergonomía:** Provee la clase `AntigravityClient` para mantener estado del socket (`port`, `token`) y simplificar exportaciones repetitivas.

### 4. Capa de Transformación y Normalización
* **Módulo:** `core/normalizer.py` (`extract_clean_messages`, `parse_iso_timestamp`, `build_clean_conversation`)
* **Naturaleza:** Funciones 100% puras (cero I/O, sin red ni dependencias externas).
* **Responsabilidad:** Aislar la conversación dialéctica (humano ↔ asistente) eliminando el ruido operacional del agente (llamadas internas a herramientas de terminal, lecturas de archivos intermedias, fallbacks de sistema y pensamientos descartados).
* **Mapeo:**
  * `CORTEX_STEP_TYPE_USER_INPUT` ➡️ `role: "user"`
  * `CORTEX_STEP_TYPE_PLANNER_RESPONSE` ➡️ `role: "assistant"`
  * Timestamps ISO con microsegundos ➡️ Segundos Unix enteros (`epoch seconds`).

### 5. Capa de Salida (Multi-formato y Persistencia)
* **Módulo:** `core/writer.py` (`get_output_dirs`, `ensure_output_dirs`, `sanitize_filename`, `build_file_base`, `save_raw_json`, `save_clean_json`, `save_markdown`, `save_conversation_bundle`)
* **Responsabilidad:** Gestionar la creación idempotente de carpetas, sanitización cross-platform de nombres de archivo y persistencia segura con codificación explícita `utf-8`.
* **Representaciones producidas simultáneamente:**
  * **Fidelidad Absoluta (`output/raw_json/`):** El payload completo tal como viaja por el socket RPC. Permite auditorías exhaustivas del funcionamiento del modelo y herramientas.
  * **Modelo Semántico (`output/clean_json/`):** Array lineal de mensajes listo para fine-tuning, análisis cognitivo o ingesta en grafos de conocimiento.
  * **Lectura Humana (`output/markdown/`):** Documento listo para Obsidian, VS Code o publicación.

### 6. Capa de Aplicación y Orquestación (Export Engine)
* **Módulo:** `core/exporter.py` (`export_conversation`, `export_all_conversations`)
* **Responsabilidad:** Coordinar el flujo completo de exportación consumiendo el cliente ConnectRPC (`core.client`), el transformador de mensajes (`core.normalizer`) y la persistencia en disco (`core.writer`).
* **Naturaleza:** Motor puramente *headless* (cero dependencias de consola o UI), desacoplado de `print` y con soporte para callbacks de progreso, permitiendo su reutilización como biblioteca en pruebas automatizadas o extensiones futuras.

### 7. Capa de Integración Externa (Adapter)
* **Archivo:** `references/chat-exporter/antigravityParser.js`
* **Responsabilidad:** Traducir los archivos de `output/clean_json/` al modelo interno consumido por el pipeline de `chat-exporter`.
* **Cumplimiento de contrato:** Implementa `extractMessages(conversation)` retornando `{ id, role, createTime, rawContent: { content_type: "text", parts: [...] } }`, permitiendo que el core de `chat-exporter` aplique sus filtros de rol, ordenamiento y generadores Markdown sin modificaciones.

---

## Módulos y Responsabilidades

### Adaptador CLI (`core/cli.py`) y Runner (`dump_antigravity.py`)
* **`dump_antigravity.py`:** Launcher ejecutable mínimo (11 líneas) cuya única función es invocar `run_cli()` y devolver el código de salida al sistema operativo.
* **`core/cli.py`:** Adaptador de presentación que encapsula la configuración de `argparse`, soporta inyección de listas de argumentos para pruebas automatizadas y renderiza la tabla formateada y el feedback visual. Expone tres modos de operación:
  1. `--list`: Visualización en tabla del catálogo completo de conversaciones registradas en la máquina.
  2. `--id <ID>`: Exportación quirúrgica de una conversación específica (soporta UUID completo o prefijo abreviado de 8 caracteres).
  3. `--all`: Procesamiento por lotes (Batch) que recorre e indexa todas las conversaciones del sistema.

### Laboratorio de Investigación (`lab/`)
Aísla las sondas desarrolladas durante la etapa de descubrimiento para no contaminar el código de producción. Se organiza en cuatro dominios de investigación:
* `lab/database/`: Scripts de prueba sobre SQLite y FTS5.
* `lab/encoding/`: Análisis de cabeceras binarias y descompresión.
* `lab/rpc_discovery/`: Búsqueda de contratos en los bundles de la extensión.
* `lab/rpc_tests/`: Validaciones de invocación directa sobre el socket.

### Documentación y Memoria (`docs/` y `planification/`)
* `planification/`: Conserva los requerimientos iniciales, reglas del proyecto y planes de acción prospectivos.
* `docs/`: Documenta con precisión arquitectónica la solución consolidada y las evidencias de laboratorio.

---

## Principios de Diseño

1. **Aislamiento del Runtime:** La herramienta interactúa con Antigravity en tiempo de ejecución a través de su interfaz oficial de red interna. No modifica archivos en disco del editor, previniendo condiciones de carrera o corrupción de datos.
2. **Idempotencia:** Ejecutar el extractor repetidas veces sobre la misma conversación produce exactamente el mismo resultado y actualiza los volcados sin duplicación ni efectos secundarios.
3. **Desacoplamiento Estricto:** Si en una versión futura Antigravity modifica su almacenamiento en disco (`.pb`, SQLite o RocksDB), la herramienta seguirá operativa mientras el Language Server mantenga su contrato ConnectRPC.


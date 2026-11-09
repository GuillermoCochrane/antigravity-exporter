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
  - [5. Capa de Salida (Multi-formato)](#5-capa-de-salida-multi-formato)
  - [6. Capa de Integración Externa (Adapter)](#6-capa-de-integración-externa-adapter)
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
references/antygravity_adapter/
├── dump_antigravity.py         # Orquestador y punto de entrada de la CLI
├── README.md                   # Documentación general y guía rápida
│
├── docs/                       # Documentación técnica retrospectiva (Estado resultante)
│   ├── ARCHITECTURE.md         # Diseño arquitectónico y módulos
│   ├── LABORATORY.md           # Registro de hipótesis, experimentos y descubrimientos
│   ├── DECISIONS.md            # Registro de decisiones arquitectónicas (ADRs)
│   ├── DATA_FLOW.md            # Diagrama del flujo y transformación de datos
│   └── INTEGRATION.md          # Especificación del contrato con chat-exporter
│
├── planification/              # Documentación prospectiva (Planes y directivas de sesión)
│   ├── plan_antigravity_adapter.md
│   ├── project_rules.md
│   ├── walkthrough_movs.md
│   └── implementation_plan_movs.md
│
├── lab/                        # Sondas de laboratorio y desensamblado
│   ├── README.md               # Catálogo descriptivo de sondas experimentales
│   ├── database/               # Inspección de bases SQLite y tablas FTS5
│   ├── encoding/               # Análisis de compresión y binarios (.pb / agy.exe)
│   ├── rpc_discovery/          # Rastreo de métodos y schemas ConnectRPC en JS
│   └── rpc_tests/              # Sondas dinámicas de invocación contra el daemon
│
└── output/                     # Almacén de artefactos exportados
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
* **Archivo:** `~/.gemini/antigravity/conversation_summaries.db`
* **Responsabilidad:** Proporcionar la lista exhaustiva de conversaciones históricas (`conversation_id`), fechas de modificación (`last_modified_time`), cantidad de pasos acumulados (`step_count`) y títulos o descripciones preliminares (`title`, `preview`).
* **Comportamiento:** Solo lectura pasiva. No altera los registros ni compite con el bloqueo de base de datos del IDE.

### 2. Capa de Descubrimiento de Socket (Daemon Hub)
* **Directorio:** `~/.gemini/antigravity/daemon/hub_*.json`
* **Responsabilidad:** Identificar dinámicamente cuál de los daemons generados por sesiones previas se encuentra activo en el sistema.
* **Mecanismo:** Ordena los descriptores por fecha de modificación descendente y ejecuta un sondeo HTTP no intrusivo con timeout de 1 segundo. El primer descriptor que devuelve estado `200` autenticado provee el puerto activo y el token CSRF para el resto de la sesión.

### 3. Capa de Comunicación (ConnectRPC Client)
* **Protocolo:** ConnectRPC sobre HTTP/1.1 (especificación estándar de Buf/gRPC).
* **Cabeceras obligatorias:**
  * `Content-Type: application/json`
  * `x-codeium-csrf-token: <CSRF_TOKEN>`
* **Endpoints consumidos:**
  * `POST /exa.language_server_pb.LanguageServerService/GetCascadeTrajectory`: Recupera el árbol con todos los pasos secuenciales de la conversación (`cascadeId`).
  * `POST /exa.language_server_pb.LanguageServerService/ConvertTrajectoryToMarkdown`: Delega en el compilador nativo del Language Server la generación del texto formateado en Markdown.

### 4. Capa de Transformación y Normalización
* **Función:** `extract_clean_messages(steps)`
* **Responsabilidad:** Aislar la conversación dialéctica (humano ↔ asistente) eliminando el ruido operacional del agente (llamadas internas a herramientas de terminal, lecturas de archivos intermedias, fallbacks de sistema y pensamientos descartados).
* **Mapeo:**
  * `CORTEX_STEP_TYPE_USER_INPUT` ➡️ `role: "user"`
  * `CORTEX_STEP_TYPE_PLANNER_RESPONSE` ➡️ `role: "assistant"`
  * Timestamps ISO con microsegundos ➡️ Segundos Unix enteros (`epoch seconds`).

### 5. Capa de Salida (Multi-formato)
La arquitectura produce simultáneamente tres representaciones con diferentes niveles de abstracción:
* **Fidelidad Absoluta (`output/raw_json/`):** El payload completo tal como viaja por el socket RPC. Permite auditorías exhaustivas del funcionamiento del modelo y herramientas.
* **Modelo Semántico (`output/clean_json/`):** Array lineal de mensajes listo para fine-tuning, análisis cognitivo o ingesta en grafos de conocimiento.
* **Lectura Humana (`output/markdown/`):** Documento listo para Obsidian, VS Code o publicación.

### 6. Capa de Integración Externa (Adapter)
* **Archivo:** `references/chat-exporter/antigravityParser.js`
* **Responsabilidad:** Traducir los archivos de `output/clean_json/` al modelo interno consumido por el pipeline de `chat-exporter`.
* **Cumplimiento de contrato:** Implementa `extractMessages(conversation)` retornando `{ id, role, createTime, rawContent: { content_type: "text", parts: [...] } }`, permitiendo que el core de `chat-exporter` aplique sus filtros de rol, ordenamiento y generadores Markdown sin modificaciones.

---

## Módulos y Responsabilidades

### CLI de Producción (`dump_antigravity.py`)
Constituye el punto de entrada ejecutable. Expone una interfaz de línea de comandos amigable que soporta tres modos de operación:
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


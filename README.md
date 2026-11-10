# Antigravity Exporter

> Extrae, decodifica y preserva conversaciones de Antigravity en formatos abiertos (Raw JSON, Clean JSON y Markdown) mediante ConnectRPC y SQLite local.

[![Versión](https://img.shields.io/badge/version-1.1.0-blue.svg)](docs/CHANGELOG.md)
[![Licencia](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](#requisitos)
[![Dependencias](https://img.shields.io/badge/dependencies-0-success.svg)](#requisitos)

**Antigravity Exporter** nació con el objetivo de rescatar y preservar el historial transaccional completo de las conversaciones desarrolladas dentro de Antigravity IDE, superando las limitaciones impuestas por la compactación de contexto y el bloqueo de archivos binarios en disco (`.pb`).

El proyecto interactúa en caliente con el daemon local de Antigravity (`agy.exe`) a través de su protocolo nativo ConnectRPC sobre HTTP, permitiendo extraer tanto los volcados crudos de la API como estructuras normalizadas compatibles con el pipeline de [AI Chat Exporter](../chat-exporter/).

---

# Índice

- [Estado](#estado)
- [Características](#características)
- [Requisitos](#requisitos)
- [Uso de la CLI](#uso-de-la-cli)
  - [Consultar versión](#consultar-versión)
  - [Listar conversaciones disponibles](#listar-conversaciones-disponibles)
  - [Exportar una conversación específica](#exportar-una-conversación-específica)
  - [Exportación masiva (Batch)](#exportación-masiva-batch)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Estructura de Salida](#estructura-de-salida)
- [Documentación](#documentación)
- [Integración con AI Chat Exporter](#integración-con-ai-chat-exporter)
- [Filosofía del Proyecto](#filosofía-del-proyecto)

---

# Estado

- ✅ **v1.1.0 (Estable):** Arquitectura Hexagonal desacoplada en capas dentro del paquete `core/`.
- ✅ Launcher ejecutable ultra-liviano (`dump_antigravity.py`, 11 líneas).
- ✅ Módulo `core/cli.py`: adaptador de terminal e intérprete de comandos con soporte para tests en memoria.
- ✅ Módulo `core/exporter.py`: motor de exportación headless / caso de uso de orquestación.
- ✅ Módulo `core/discovery.py`: descubrimiento dinámico de socket y token CSRF (`hub_*.json`).
- ✅ Módulo `core/database.py`: consultas aisladas a SQLite `conversation_summaries.db`.
- ✅ Módulo `core/client.py`: transporte ConnectRPC sobre HTTP y cliente `AntigravityClient`.
- ✅ Módulo `core/normalizer.py`: funciones 100% puras de normalización (listas para testing con fixtures).
- ✅ Módulo `core/writer.py`: persistencia atómica y gestión de rutas seguras en disco.
- ✅ Extracción masiva comprobada (100% de éxito en 30 sesiones históricas y sesiones masivas de +16.000 pasos).
- ✅ Triple formato de salida simultáneo (`raw_json`, `clean_json`, `markdown`).
- ✅ Adapter integrado para el pipeline de `chat-exporter` (`antigravityParser.js`).
- ✅ Suite documental técnica completa (ADRs, Laboratorio, Arquitectura, Testing Manual, Changelog y Roadmap).

---

# Características

- **Extracción sin desensamblado binario destructivo:** Se conecta directamente al socket local del Language Server Daemon, garantizando cero riesgo de corrupción de datos.
- **Triple nivel de fidelidad simultáneo:**
  * `raw_json`: Árbol íntegro con cada detalle de la API, herramientas y pensamientos.
  * `clean_json`: Mensajes dialécticos depurados (`id`, `role`, `timestamp`, `text`).
  * `markdown`: Documento formateado oficialmente por el motor nativo de Antigravity.
- **Portabilidad absoluta:** Construido 100% con la biblioteca estándar de Python 3 (sin `pip install` ni dependencias externas).
- **Interoperabilidad:** Adaptador listo para ser consumido por el motor de `chat-exporter`.

---

# Requisitos

- Python 3.8 o superior.
- Antigravity IDE o la CLI de Antigravity abierta (para mantener el Language Server Daemon activo en `127.0.0.1`).

---

# Uso de la CLI

Desde la raíz del repositorio:

### Consultar versión
Muestra la versión actual del ejecutable:

```bash
python dump_antigravity.py --version
```

### Listar conversaciones disponibles
Muestra el catálogo completo de conversaciones registradas en la máquina con su ID, cantidad de pasos, fecha y título:

```bash
python dump_antigravity.py --list
```

### Exportar una conversación específica
Permite exportar una conversación pasando su UUID completo o su prefijo de 8 caracteres:

```bash
python dump_antigravity.py --id eacc4ff1
```

### Exportación masiva (Batch)
Recorre y exporta la totalidad de las conversaciones del sistema en una única pasada:

```bash
python dump_antigravity.py --all
```

---

# Estructura del Proyecto

```text
antigravity-exporter/
├── dump_antigravity.py         # Launcher mínimo ejecutable (11 líneas)
├── README.md                   # Documentación principal de bienvenida
├── LICENSE                     # Licencia pública MIT
├── .gitignore                  # Reglas de exclusión (aislamiento estricto de output/)
│
├── core/                       # Paquete del sistema (Arquitectura Hexagonal en capas)
│   ├── __init__.py             # Single source of truth para la versión del paquete
│   ├── cli.py                  # Adaptador CLI: Intérprete de consola y formateo de tablas
│   ├── client.py               # Capa 3: Cliente ConnectRPC y transporte HTTP
│   ├── database.py             # Capa 1: Catálogo y consultas SQLite
│   ├── discovery.py            # Capa 2: Descubrimiento de socket y validación de daemon
│   ├── exporter.py             # Capa 6: Motor headless de exportación (Pipeline)
│   ├── normalizer.py           # Capa 4: Transformación pura de payload a Clean JSON
│   └── writer.py               # Capa 5: Persistencia segura y gestión de rutas en disco
│
├── docs/                       # Documentación técnica retrospectiva (Estado resultante)
│   ├── ARCHITECTURE.md         # Diseño arquitectónico y módulos de 6 capas
│   ├── CHANGELOG.md            # Registro de evolución histórica y versiones
│   ├── DATA_FLOW.md            # Diagrama del flujo y transformación de datos
│   ├── DECISIONS.md            # Registro de decisiones arquitectónicas (ADRs)
│   ├── INTEGRATION.md          # Especificación del contrato con chat-exporter
│   ├── LABORATORY.md           # Registro de hipótesis (H-001 a H-006) y experimentos
│   ├── MANUAL_TESTING.md       # Casos y evidencias de pruebas manuales por versión
│   └── ROADMAP.md              # Estado actual y próximos hitos planificados
│
├── planification/              # Documentación prospectiva y metodología
│   ├── rules/                  # Reglas de workflow, sprints y commit templates (ignorado en git)
│   ├── 00-inicial/             # Documentación prospectiva fundacional (v1.0.0)
│   └── 01-modularizacion/      # Sprint 01: Walkthrough y planes de implementación por módulo
│
├── lab/                        # Laboratorio de ingeniería inversa (40 sondas auxiliares)
│   ├── README.md               # Catálogo descriptivo de sondas
│   ├── database/               # Inspección de SQLite y FTS5
│   ├── encoding/               # Análisis de binarios y compresión (.pb)
│   ├── rpc_discovery/          # Rastreo de métodos ConnectRPC en JS
│   └── rpc_tests/              # Sondas dinámicas de invocación
│
└── output/                     # Almacén de salidas exportadas (excluido de git)
    ├── raw_json/               # Payloads crudos de la API
    ├── clean_json/             # Diálogos normalizados
    └── markdown/               # Documentos Markdown oficiales
```

---

# Estructura de Salida

Cada exportación genera automáticamente tres archivos en `output/`:

1. **`output/raw_json/<id>.raw.json`:**  
   El volcado exacto del objeto `trajectory` devuelto por el socket RPC.
2. **`output/clean_json/<fecha>_<titulo>_<id>.clean.json`:**  
   Estructura limpia con roles unificados (`user` y `assistant`) y timestamps en segundos Unix.
3. **`output/markdown/<fecha>_<titulo>_<id>.md`:**  
   Documento Markdown oficial generado por el compilador de Antigravity.

---

# Documentación

La documentación del proyecto se organiza por responsabilidad bajo el principio de documentar el estado resultante:

| Documento | Propósito |
|---|---|
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Organización interna del sistema, capas y diagramas de componentes. |
| [CHANGELOG](docs/CHANGELOG.md) | Registro de evolución histórica y cambios por versión. |
| [LABORATORY](docs/LABORATORY.md) | Registro de hipótesis (`H-001` a `H-006`), experimentos y descubrimientos técnicos de las sondas de `lab/`. |
| [DECISIONS](docs/DECISIONS.md) | Registro de decisiones de arquitectura (ADRs) con contexto y consecuencias. |
| [DATA_FLOW](docs/DATA_FLOW.md) | Recorrido conceptual de los datos desde la memoria de Antigravity hasta el Markdown final. |
| [INTEGRATION](docs/INTEGRATION.md) | Contratos de datos, especificación del esquema y uso del Adapter para `chat-exporter`. |
| [ROADMAP](docs/ROADMAP.md) | Estado actual del proyecto y planificación de próximos hitos evolutivos. |

---

# Integración con AI Chat Exporter

Para procesar los archivos `clean_json` generados a través del pipeline de `chat-exporter` (aplicando filtros de roles, modo compacto o exportadores adicionales):

1. El adaptador se encuentra listo en [`references/chat-exporter/antigravityParser.js`](../chat-exporter/antigravityParser.js).
2. Se ejecuta con Node.js sobre el pipeline existente:
   ```bash
   node references/chat-exporter/test_antigravity_pipeline.js
   ```

---

# Filosofía del Proyecto

- **KISS:** Resolver mediante la interfaz de red local en vez de ingeniería inversa destructiva de archivos en disco.
- **DRY:** Reutilizar el compilador nativo de Markdown provisto por el Language Server.
- **SRP:** Desacoplamiento estricto entre catálogo, transporte RPC, normalización y renderizado.
- **Preservación Inmutable:** La fuente de la verdad (RAW JSON) se almacena intacta para garantizar reproducibilidad a futuro.

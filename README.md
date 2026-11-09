# Antigravity Exporter

> Extrae, decodifica y preserva conversaciones de Antigravity en formatos abiertos (Raw JSON, Clean JSON y Markdown) mediante ConnectRPC y SQLite local.

[![Versión](https://img.shields.io/badge/version-1.0.0-blue.svg)](docs/CHANGELOG.md)
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

- ✅ **v1.0.0 (Estable):** Versión fundacional completa y testeada.
- ✅ CLI funcional con soporte para versión (`dump_antigravity.py --version`).
- ✅ Descubrimiento dinámico de sockets y tokens CSRF (`hub_*.json`).
- ✅ Extracción masiva comprobada (100% de éxito en 30 sesiones históricas).
- ✅ Soporte para sesiones masivas (+15.000 pasos recuperados).
- ✅ Triple formato de salida simultáneo (`raw_json`, `clean_json`, `markdown`).
- ✅ Adapter integrado para el pipeline de `chat-exporter` (`antigravityParser.js`).
- ✅ Suite documental técnica completa (ADRs, Laboratorio, Arquitectura, Changelog y Roadmap).

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
├── dump_antigravity.py         # Entry point de la CLI de producción
├── README.md                   # Documentación principal de bienvenida
├── LICENSE                     # Licencia pública MIT
├── .gitignore                  # Reglas de exclusión (aislamiento estricto de output/)
│
├── docs/                       # Documentación técnica retrospectiva (Estado resultante)
│   ├── ARCHITECTURE.md         # Diseño arquitectónico y módulos de 6 capas
│   ├── CHANGELOG.md            # Registro de evolución histórica y versiones
│   ├── DATA_FLOW.md            # Diagrama del flujo y transformación de datos
│   ├── DECISIONS.md            # Registro de decisiones arquitectónicas (ADRs)
│   ├── INTEGRATION.md          # Especificación del contrato con chat-exporter
│   ├── LABORATORY.md           # Registro de hipótesis (H-001 a H-006) y experimentos
│   └── ROADMAP.md              # Estado actual y próximos hitos planificados
│
├── planification/              # Documentación prospectiva (Planes y directivas de sesión)
│   ├── plan_antigravity_adapter.md
│   ├── project_rules.md
│   ├── roadmap.md
│   ├── plan.md
│   ├── devolucion.md
│   └── org1.md
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

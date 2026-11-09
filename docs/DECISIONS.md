# Registro de decisiones

---

## ADR-0001

#### Fecha

2026-11-08

#### Título

Extracción vía ConnectRPC en lugar de desensamblado binario de archivos `.pb`.

#### Motivación

Los historiales de conversación recientes de Antigravity se persisten en archivos con extensión `.pb` de más de 40 MB ubicados en `~/.gemini/antigravity/conversations/`. El análisis de entropía demostró que estos archivos no corresponden a volcados simples comprimidos con `gzip` o `zlib`, sino a serializaciones binarias propietarias administradas dinámicamente por el proceso compilado en Go (`agy.exe`).

Intentar leer y descomprimir estos archivos directamente en disco implicaba:
1. Revertir formatos binarios internos susceptibles de cambiar entre actualizaciones menores del IDE.
2. Riesgo de inconsistencia o corrupción si el proceso principal escribe concurrentemente sobre el archivo.
3. Pérdida de la lógica oficial de resolución de dependencias entre pasos (`steps`).

#### Decisión

Interactuar en tiempo de ejecución con el Language Server Daemon de Antigravity mediante su protocolo oficial **ConnectRPC** sobre HTTP (`/exa.language_server_pb.LanguageServerService/GetCascadeTrajectory`), reutilizando el canal local autenticado provisto por el descriptor `hub_<port>.json`.

#### Consecuencia

- Se obtiene el 100% de la información estructurada y validada directamente por el propio motor oficial sin riesgo de corrupción.
- Se desacopla la herramienta del formato físico de almacenamiento subyacente (`.pb`, SQLite o RocksDB).
- Requiere que Antigravity IDE o la CLI de Antigravity se encuentren abiertos durante la ejecución de la extracción para mantener el daemon activo.

#### Estado

Aceptada.

---

## ADR-0002

#### Fecha

2026-11-08

#### Título

Triple nivel de fidelidad de salida (`raw_json`, `clean_json`, `markdown`).

#### Motivación

Los casos de uso para las conversaciones archivadas son heterogéneos y tienen requerimientos técnicos contradictorios:
1. **Auditoría y respaldo:** Requiere el árbol íntegro de llamadas a herramientas (`tool_calls`), parámetros JSON, metadatos y pensamientos del agente sin ninguna pérdida de fidelidad.
2. **Entrenamiento y análisis cognitivo:** Requiere una estructura lineal limpia y estandarizada de mensajes (humano ↔ asistente), descartando ruido operacional.
3. **Lectura humana y portabilidad:** Requiere un documento de texto con formato Markdown legible en cualquier visor o editor (Obsidian, VS Code).

Intentar unificar las tres necesidades en un único archivo generaba documentos difíciles de parsear o con pérdida irreversible de datos.

#### Decisión

Generar simultáneamente tres archivos independientes por cada conversación exportada, organizados en subcarpetas especializadas:
- `output/raw_json/`: El volcado íntegro devuelto por el socket RPC.
- `output/clean_json/`: Mensajes limpios normalizados (`id`, `role`, `timestamp`, `text`).
- `output/markdown/`: Documento Markdown oficial renderizado por `ConvertTrajectoryToMarkdown`.

#### Consecuencia

Cada caso de uso consume la capa de abstracción adecuada sin necesidad de realizar re-procesamientos o peticiones adicionales de red.

#### Estado

Aceptada.

---

## ADR-0003

#### Fecha

2026-11-08

#### Título

Aislamiento de sondas experimentales en directorio `lab/`.

#### Motivación

Durante la fase de investigación se desarrollaron más de 35 scripts de prueba (lectura de cabeceras, escaneo de procesos WMI, desensamblado de código empaquetado, pruebas de compresión). Mantener estos archivos en la raíz del proyecto generaba contaminación visual, dificultaba identificar el entry point productivo y violaba el principio de responsabilidad única.

Sin embargo, eliminar estos scripts hubiera destruido la evidencia técnica que respalda las decisiones de arquitectura y la posibilidad de reproducir las hipótesis documentadas.

#### Decisión

Reubicar la totalidad de las sondas en un directorio dedicado `lab/`, clasificándolas según su dominio técnico:
- `lab/database/` (SQLite y FTS5).
- `lab/encoding/` (Binarios y compresión).
- `lab/rpc_discovery/` (Rastreo de interfaces en JS).
- `lab/rpc_tests/` (Invocaciones dinámicas contra el socket).

En la raíz del proyecto se preserva únicamente la CLI de producción (`dump_antigravity.py`), su `README.md` y las carpetas de salida y documentación.

#### Consecuencia

El proyecto conserva una raíz de producción limpia y profesional, a la vez que preserva el 100% de la memoria de investigación en un laboratorio ordenado y catalogado.

#### Estado

Aceptada.

---

## ADR-0004

#### Fecha

2026-11-08

#### Título

Patrón Adapter para interoperabilidad con `chat-exporter`.

#### Motivación

El proyecto `chat-exporter` cuenta con un pipeline consolidado y probado (`filter` ➡️ `normalizer` ➡️ `markdown` ➡️ `writer`) con selectores de modo compacto, filtros de roles y formateo de citas. Incorporar la lógica específica de Antigravity dentro del núcleo de `chat-exporter` hubiera introducido acoplamiento indeseado y violado el principio Open/Closed.

#### Decisión

Implementar un componente Adapter (`references/chat-exporter/antigravityParser.js`) que traduce el esquema producido en `output/clean_json/` al modelo interno consumido por el pipeline de `chat-exporter`, implementando la función contractual `extractMessages(conversation)`.

#### Consecuencia

- El núcleo de `chat-exporter` se mantiene agnóstico y cerrado a modificaciones.
- Las conversaciones de Antigravity se pueden procesar con las mismas opciones avanzadas de la CLI de `chat-exporter` (filtros, modo compacto, templates) que las provenientes de ChatGPT o Joi.ai.

#### Estado

Aceptada.

---

## ADR-0005

#### Fecha

2026-11-08

#### Título

Cero dependencias externas en tiempo de ejecución (Python Standard Library).

#### Motivación

La instalación de librerías externas de terceros (como clientes pesados de gRPC, drivers compilados de SQLite o frameworks HTTP) introduce dependencias de entorno (`venv`, `pip`), potenciales problemas de compatibilidad entre versiones de Windows y necesidad de herramientas de compilación en C++.

Dado que el protocolo ConnectRPC de Antigravity admite peticiones JSON sobre HTTP estándar, no se requiere ninguna funcionalidad ausente en la biblioteca estándar de Python.

#### Decisión

Construir la herramienta de extracción utilizando exclusivamente módulos nativos de Python 3:
- `urllib.request` y `urllib.error` para transporte HTTP.
- `sqlite3` para consultas pasivas de catálogo y metadatos.
- `json` para codificación y decodificación de payloads.
- `argparse` para la interfaz de línea de comandos.
- `re`, `datetime`, `os` y `glob` para utilidades auxiliares.

#### Consecuencia

La herramienta es portátil de forma inmediata en cualquier máquina que posea Python 3 instalado, con cero pasos de configuración previa o descargas de paquetes.

#### Estado

Aceptada.


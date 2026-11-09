# Laboratory

## Índice

- [Hipótesis](#hipótesis)
  - [H-001 — Descompresión estándar de archivos `.pb`](#h-001--descompresión-estándar-de-archivos-pb)
  - [H-002 — Almacenamiento íntegro en SQLite (`conversation_summaries.db`)](#h-002--almacenamiento-íntegro-en-sqlite-conversation_summariesdb)
  - [H-003 — Existencia de un Daemon local en memoria](#h-003--existencia-de-un-daemon-local-en-memoria)
  - [H-004 — Protocolo de comunicación del Language Server (ConnectRPC)](#h-004--protocolo-de-comunicación-del-language-server-connectrpc)
  - [H-005 — Identificador de consulta en `ConvertTrajectoryToMarkdown`](#h-005--identificador-de-consulta-en-converttrajectorytomarkdown)
  - [H-006 — Parámetro de acceso para el historial completo (`cascadeId`)](#h-006--parámetro-de-acceso-para-el-historial-completo-cascadeid)
- [Experimentos](#experimentos)
  - [E-001 — Análisis de entropía y descompresión de archivos `.pb`](#e-001--análisis-de-entropía-y-descompresión-de-archivos-pb)
  - [E-002 — Inspección de índices FTS5 y metadatos relacionales](#e-002--inspección-de-índices-fts5-y-metadatos-relacionales)
  - [E-003 — Rastreo de sockets y procesos activos del entorno](#e-003--rastreo-de-sockets-y-procesos-activos-del-entorno)
  - [E-004 — Desensamblado de métodos RPC en el frontend (`extension.js`)](#e-004--desensamblado-de-métodos-rpc-en-el-frontend-extensionjs)
  - [E-005 — Negociación de llamadas HTTP contra el daemon ConnectRPC](#e-005--negociación-de-llamadas-http-contra-el-daemon-connectrpc)
  - [E-006 — Prueba de estrés de extracción completa (Sesión de 15.000+ pasos)](#e-006--prueba-de-estrés-de-extracción-completa-sesión-de-15000-pasos)
- [Descubrimientos](#descubrimientos)
  - [Arquitectura de Almacenamiento](#arquitectura-de-almacenamiento)
  - [Protocolo y Seguridad de Red Local](#protocolo-y-seguridad-de-red-local)
  - [Topología del Modelo de Conversación](#topología-del-modelo-de-conversación)

---

## Hipótesis

### H-001 — Descompresión estándar de archivos `.pb`

#### Objetivo
Verificar si los archivos de conversación con extensión `.pb` ubicados en `~/.gemini/antigravity/conversations/` corresponden a volcados de Protocol Buffers serializados y comprimidos con algoritmos estándar (`gzip`, `zlib`, `snappy`, `zstd`).

#### Estado
✖ Refutada.

#### Evidencia
* La inspección de cabeceras mediante `test_pb_encoding.py` arrojó errores de formato (`Error -3: incorrect header check`).
* Un muestreo de 100 KB en archivos estables arrojó solo 76 cadenas de caracteres imprimibles de 5 o más letras (`check_inactive_pb.py`).
* La entropía de la muestra es prácticamente idéntica a ruido pseudoaleatorio (> 7.9 bits/byte), lo que evidencia un formato binario propietario administrado en caliente o cifrado por el runtime.

#### Conclusión
No es viable extraer de forma determinista el historial completo mediante scripts de descompresión en frío sin revertir la lógica interna de serialización del binario compiled Go (`agy.exe`).

*Sondas asociadas:* `lab/encoding/check_compressors.py`, `lab/encoding/check_pb_type.py`, `lab/encoding/check_inactive_pb.py`, `lab/encoding/test_pb_encoding.py`.

---

### H-002 — Almacenamiento íntegro en SQLite (`conversation_summaries.db`)

#### Objetivo
Determinar si la base de datos central `conversation_summaries.db` aloja el texto íntegro de los turnos de las conversaciones para su indexación.

#### Estado
⚠️ Parcial.

#### Evidencia
* La tabla virtual `conversations_fts` implementada con FTS5 (`conversations_fts_content`) almacena columnas `user_body` y `agent_body`.
* La lectura de fragmentos mediante `inspect_all_chunks.py` demostró que los mensajes no se almacenan como registros atómicos estructurados, sino en bloques compactados (`chunks` de texto acumulado).
* Falta información crítica de contexto: jerarquía de turnos, estado de herramientas (`tool_calls`), timestamps granulares por mensaje y diferenciación de subagentes.

#### Conclusión
La base de datos SQLite permite reconstruir resúmenes y buscar texto, pero resulta insuficiente para una extracción estructurada con fidelidad transaccional.

*Sondas asociadas:* `lab/database/inspect_db.py`, `lab/database/find_fts_mention.py`, `lab/database/read_fts_chunk0.py`, `lab/database/inspect_all_chunks.py`.

---

### H-003 — Existencia de un Daemon local en memoria

#### Objetivo
Verificar si Antigravity mantiene en ejecución un proceso servidor de soporte que sostenga la sesión activa y gestione el acceso a las conversaciones en memoria.

#### Estado
✔ Confirmada.

#### Evidencia
* El escaneo de procesos del sistema reveló la ejecución de `C:\Users\cochr\.gemini\bin\agy.exe`.
* En la carpeta de ejecución `~/.gemini/antigravity/daemon/` se identificaron archivos descriptor `hub_<port>.json`.
* La sonda `test_daemons.py` comprobó que el archivo `hub_61301.json` correspondía a un socket activo que devolvió respuesta exitosa `HTTP 200` ante peticiones autenticadas.

#### Conclusión
Existe un servidor Language Server Daemon corriendo en `127.0.0.1` bajo control de `agy.exe`, configurado mediante un token de acceso temporal por sesión.

*Sondas asociadas:* `lab/rpc_tests/test_daemons.py`, `lab/rpc_tests/read_hub61301.py`.

---

### H-004 — Protocolo de comunicación del Language Server (ConnectRPC)

#### Objetivo
Determinar el mecanismo de transporte y la interfaz utilizada por la extensión del editor para comunicarse con el Language Server Daemon.

#### Estado
✔ Confirmada.

#### Evidencia
* La inspección estática del bundle del frontend (`agy/dist/extension.js`) reveló el uso de `createConnectTransport` configurado con HTTP/1.1 y HTTP/2.
* Todas las llamadas salientes inyectan la cabecera `x-codeium-csrf-token` leída desde el descriptor del daemon.
* El servicio principal está registrado bajo el paquete gRPC/Protobuf `exa.language_server_pb.LanguageServerService`.
* El protocolo ConnectRPC admite de forma nativa peticiones `POST` con cuerpo JSON (`application/json`), sin necesidad de compilar stubs binarios.

#### Conclusión
Cualquier cliente HTTP estándar puede invocar los procedimientos del daemon siempre que conozca el puerto asignado, el token CSRF y el esquema del payload.

*Sondas asociadas:* `lab/rpc_discovery/find_rpc_client.py`, `lab/rpc_discovery/find_lss.py`, `lab/rpc_discovery/find_service_paths.py`.

---

### H-005 — Identificador de consulta en `ConvertTrajectoryToMarkdown`

#### Objetivo
Verificar si el procedimiento `ConvertTrajectoryToMarkdown` acepta el identificador visible de la conversación (`conversationId` / `cascadeId`) para generar el documento Markdown.

#### Estado
✖ Refutada.

#### Evidencia
* Al invocar el endpoint pasando `{ "trajectoryId": "1cfae999-..." }`, el servidor devolvió `HTTP 404: not_found: trajectory not found`.
* El análisis del schema (`GetConversationMetadata`) demostró que Antigravity distingue entre dos entidades:
  * `cascadeId`: El identificador de la conversación (persistente a lo largo de las sesiones).
  * `trajectoryId`: El identificador interno del árbol de pasos de ejecución correspondiente a dicha conversación.

#### Conclusión
Para exportar a Markdown es obligatorio resolver previamente el `trajectoryId` consultando el árbol de la conversación mediante su `cascadeId`.

*Sondas asociadas:* `lab/rpc_tests/test_rpc_calls.py`, `lab/rpc_tests/test_rpc_markdown.py`.

---

### H-006 — Parámetro de acceso para el historial completo (`cascadeId`)

#### Objetivo
Determinar si el endpoint `GetCascadeTrajectory` permite recuperar la totalidad de pasos de una conversación utilizando su `cascadeId`.

#### Estado
✔ Confirmada.

#### Evidencia
* La llamada `POST /exa.language_server_pb.LanguageServerService/GetCascadeTrajectory` enviando `{"cascadeId": "1cfae999-..."}` devolvió una respuesta `HTTP 200` con 15.187 pasos estructurados.
* El cuerpo JSON contiene el desglose secuencial de cada paso con su tipo (`CORTEX_STEP_TYPE_USER_INPUT`, `CORTEX_STEP_TYPE_PLANNER_RESPONSE`, etc.), marcas temporales, contenido textual y metadatos.

#### Conclusión
`GetCascadeTrajectory` es la puerta de acceso canónica para obtener el árbol de datos completo y decodificado de cualquier conversación de Antigravity.

*Sondas asociadas:* `lab/rpc_tests/inspect_cascade_trajectory.py`, `lab/rpc_tests/inspect_steps_detail.py`.

---

## Experimentos

### E-001 — Análisis de entropía y descompresión de archivos `.pb`

#### Objetivo
Intentar leer de forma directa los archivos `.pb` de `conversations/` usando Python nativo.

#### Procedimiento
1. Se construyó la sonda `lab/encoding/check_compressors.py` para constatar los módulos de descompresión disponibles en el entorno.
2. Se construyó `lab/encoding/test_pb_encoding.py` para evaluar bloques de datos de `1cfae999...pb` contra `zlib` y `gzip`.
3. Se analizó la frecuencia de caracteres y patrones de texto en sesiones inactivas con `lab/encoding/check_inactive_pb.py`.

#### Resultado
Fallido. Los formatos estándar de compresión fueron rechazados de forma consistente. La densidad de strings imprimibles fue inferior al 0.08%, descartando texto plano serializado sin compresión o empaquetado directo.

#### Conclusión
Se abandonó la estrategia de desensamblado binario directo a favor de explorar la capa de comunicación del proceso en ejecución.

---

### E-002 — Inspección de índices FTS5 y metadatos relacionales

#### Objetivo
Explorar el contenido estructurado de `conversation_summaries.db` para evaluar si el historial completo residía en SQLite.

#### Procedimiento
1. Se ejecutó `lab/database/inspect_db.py` enumerando todas las tablas (`conversation_summaries`, `conversations_fts`, `conversations_fts_docsize`, etc.).
2. Se analizaron las columnas de la tabla virtual FTS5 (`user_body`, `agent_body`).
3. Se ejecutó `lab/database/inspect_all_chunks.py` para medir la extensión y partición de las cadenas almacenadas.

#### Resultado
Parcial. Se confirmó que la base conserva el catálogo de todas las conversaciones (30 sesiones registradas) con fecha de modificación, URIs de workspaces y títulos. Sin embargo, el texto en FTS5 se encuentra consolidado en fragmentos continuos sin división por turnos individuales.

#### Conclusión
`conversation_summaries.db` debe ser utilizada como índice maestro de metadatos (IDs, fechas, títulos), pero no como fuente primaria del contenido transaccional.

---

### E-003 — Rastreo de sockets y procesos activos del entorno

#### Objetivo
Descubrir los endpoints de red local expuestos por el sistema mientras el editor se encuentra abierto.

#### Procedimiento
1. Se inspeccionó la tabla de procesos mediante PowerShell/WMI buscando binarios vinculados a Antigravity. Se identificó el proceso `agy.exe` (PID 24048).
2. Se analizó el directorio `~/.gemini/antigravity/daemon/` hallando múltiples archivos de configuración de daemons anteriores y actuales (`hub_*.json`).
3. Se implementó `lab/rpc_tests/test_daemons.py` para realizar un sondeo por polling HTTP contra cada puerto reportado, utilizando el token provisto en el descriptor.

#### Resultado
Exitoso. Se constató que el socket `http://127.0.0.1:61301` respondió con código `200` y validó la autenticación provista por `x-codeium-csrf-token: 6687a388-...`.

#### Conclusión
Se obtuvo un canal de comunicación directo y autenticado con el motor interno de Antigravity sin violar las políticas de seguridad del proceso.

---

### E-004 — Desensamblado de métodos RPC en el frontend (`extension.js`)

#### Objetivo
Mapear los nombres de los procedimientos RPC expuestos por el daemon y sus contratos de datos.

#### Procedimiento
1. Se escaneó estáticamente el bundle empaquetado de la extensión (`resources/app/extensions/agy/dist/extension.js`) mediante expresiones regulares con `lab/rpc_discovery/search_code.py` y `find_service_paths.py`.
2. Se detectaron referencias a la arquitectura Protobuf y los servicios generados (`LanguageServerService`).
3. Se aislaron las rutas completas del servicio:
   * `/exa.language_server_pb.LanguageServerService/GetCascadeTrajectory`
   * `/exa.language_server_pb.LanguageServerService/ConvertTrajectoryToMarkdown`
   * `/exa.language_server_pb.LanguageServerService/GetConversationMetadata`

#### Resultado
Exitoso. Se obtuvieron las rutas absolutas exactas requeridas por la especificación ConnectRPC.

#### Conclusión
No fue necesario inferir nombres de métodos ni realizar ataques por fuerza bruta: los identificadores de servicio quedaron plenamente documentados a partir del propio cliente del editor.

---

### E-005 — Negociación de llamadas HTTP contra el daemon ConnectRPC

#### Objetivo
Validar la estructura de payload esperada por cada método y obtener respuestas válidas en formato JSON.

#### Procedimiento
1. Se escribió `lab/rpc_tests/test_rpc_calls.py` realizando peticiones POST contra `GetConversationMetadata`, `GetCascadeTrajectory` y `ConvertTrajectoryToMarkdown`.
2. Se iteraron los nombres de parámetros ante respuestas `400 Invalid Argument` emitidas por el servidor ConnectRPC.
3. Se comprobó la asociación biyectiva entre `cascadeId` y `trajectoryId`.

#### Resultado
Exitoso. Al invocar `GetCascadeTrajectory` con `{"cascadeId": "<ID>"}`, el servidor devolvió el árbol íntegro en JSON legible. A su vez, utilizando el `trajectoryId` devuelto por dicha estructura, se logró invocar `ConvertTrajectoryToMarkdown` obteniendo el texto formateado oficial.

#### Conclusión
Se logró la extracción programática del 100% de la información de cualquier conversación mediante llamadas JSON estándar sobre HTTP local.

---

### E-006 — Prueba de estrés de extracción completa (Sesión de 15.000+ pasos)

#### Objetivo
Poner a prueba la robustez del mecanismo ante la conversación de mayor tamaño registrada en el entorno (`1cfae999-9108-4b5e-955e-667dd3eeee89`).

#### Procedimiento
1. Se ejecutó `lab/rpc_tests/inspect_cascade_trajectory.py` con un timeout extendido (30 segundos).
2. Se midió el volumen de datos transferido y la integridad de los pasos desde el inicio (febrero de 2026) hasta el estado actual.
3. Se verificó la generación del documento Markdown mediante `ConvertTrajectoryToMarkdown`.

#### Resultado
Exitoso. El daemon transfirió los 15.187 pasos sin cortes de conexión ni desbordamientos de memoria. El convertidor generó un archivo Markdown coherente de 85.750 caracteres y 1.471 líneas.

#### Conclusión
El método demostró ser escalable y resistente incluso en historiales masivos que bloqueaban la interfaz visual del IDE.

---

## Descubrimientos

### Arquitectura de Almacenamiento
* Antigravity persiste las trayectorias en archivos de extensión `.pb` gestionados exclusivamente por el runtime compilado en Go (`agy.exe`).
* Los historiales no deben manipularse directamente en disco mientras el daemon se encuentra operativo, dado que las escrituras son asíncronas y concurrentes.
* El archivo `conversation_summaries.db` cumple la función de registro relacional de alto nivel (catálogo), ideal para poblar selectores, listados y paneles de control.

### Protocolo y Seguridad de Red Local
* El daemon levanta dinámicamente un puerto HTTP no privilegiado en cada inicio de sesión, documentando el puerto asignado y un token de un solo uso en `daemon/hub_<port>.json`.
* La autenticación requiere estricta coincidencia de la cabecera HTTP:
  ```http
  x-codeium-csrf-token: <TOKEN_DEL_HUB>
  Content-Type: application/json
  ```
* Las peticiones cursadas sin dicha cabecera son rechazadas a nivel socket antes de evaluar el endpoint.

### Topología del Modelo de Conversación
* Existe una diferenciación estructural entre:
  * **`cascadeId`**: Clave pública permanente que identifica la sesión o hilo de conversación (el UUID mostrado en la UI y registrado en `conversation_summaries.db`).
  * **`trajectoryId`**: Identificador interno del grafo de ejecución actual, generado y resuelto por el backend.
* El modelo de pasos (`steps`) es polimórfico:
  * Pasos de usuario: identificados con `CORTEX_STEP_TYPE_USER_INPUT`, con el texto residiendo en `userInput.userResponse` o `userInput.items[].text`.
  * Pasos del modelo: identificados con `CORTEX_STEP_TYPE_PLANNER_RESPONSE`, con el contenido en `plannerResponse.response` y las acciones registradas en `plannerResponse.toolCalls`.


# Laboratorio de Ingeniería Inversa y Sondas (`lab/`)

Esta carpeta contiene todas las sondas experimentales desarrolladas para descubrir la arquitectura interna, formatos de almacenamiento y puertos de comunicación de Antigravity.

---

## Estructura por Responsabilidad

### 📁 `database/` (Análisis de SQLite y FTS)
Scripts dedicados a inspeccionar las bases de datos locales:
- `inspect_db.py`: Análisis de tablas y esquemas de `conversation_summaries.db`.
- `inspect_sample_db.py`: Lectura de los esquemas `.db` antiguos de conversaciones (`steps`, `trajectory_meta`).
- `inspect_vscdb.py`: Inspección de `state.vscdb` en el almacenamiento global del IDE.
- `list_all_convs.py`: Listado crudo de todas las conversaciones registradas.
- `find_fts_mention.py`: Búsqueda de menciones específicas dentro de los índices FTS5.
- `read_fts_chunk0.py`: Lectura y decodificación del primer chunk en FTS5.
- `inspect_all_chunks.py`: Análisis de la partición de mensajes por chunks de FTS.

### 📁 `encoding/` (Análisis de Binarios, Compresión y Protobuf)
Sondas creadas para investigar la serialización de los archivos `.pb`:
- `check_compressors.py`: Chequeo de librerías de compresión instaladas en Python.
- `check_pb_type.py`: Detección de encabezados y firmas de archivos binarios.
- `check_inactive_pb.py`: Comparación de entropía y consistencia entre sesiones activas e inactivas.
- `test_pb_encoding.py`: Pruebas de descompresión con zlib, gzip y extracción de cadenas ASCII.
- `inspect_pb.py`: Lectura de cabeceras crudas en hexadecimal y representación de bytes.
- `scan_agy_exe.py`: Escaneo de patrones criptográficos y de compresión en el binario `agy.exe`.

### 📁 `rpc_discovery/` (Descubrimiento y Desensamblado de Métodos)
Scripts que buscaron las definiciones de ConnectRPC en los archivos JavaScript del IDE (`extension.js`, `bridge.js`) y binarios:
- `find_service_methods.py`: Detección de la clase `LanguageServerService` y creación del cliente RPC.
- `find_rpc_endpoints.py`: Mapeo de métodos como `ConvertTrajectoryToMarkdown` y `GetTrajectoryTurns`.
- `find_rpc_calls.py`: Rastreo de llamadas de red dentro de la extensión.
- `find_service_name.py`: Identificación de los nombres de los esquemas Protobuf.
- `find_service_paths.py`: Búsqueda de URLs absolutas `/exa.language_server_pb.LanguageServerService/...`.
- `find_lss.py`: Búsqueda de apariciones de la interfaz del Language Server.
- `find_wh.py`: Rastreo de descriptores en tablas minificadas.
- `find_pkg.py`: Detección de prefijos de paquetes Protobuf.
- `find_req_fields.py`: Búsqueda de campos esperados por cada estructura de petición.
- `find_req_schema.py`: Análisis del descriptor de peticiones.
- `find_cn.py`: Rastreo de referencias minificadas del Request Schema.
- `find_convert_vscode.py`: Verificación de referencias cruzadas en el bridge de VS Code.
- `find_convert.py`: Búsqueda de manejadores de conversión.
- `find_pb_read.py` / `find_pb_vscode.py`: Búsqueda de manipuladores de archivos `.pb`.
- `find_service_schema.py`: Inspección de interfaces de servicio.
- `find_rpc_client.py`: Inspección del método constructor `getRpcClient()`.
- `search_schema_def.py`: Búsqueda de esquemas de petición en `dist/extension.js`.
- `search_code.py`: Búsqueda de menciones de Trajectory en binarios y código.

### 📁 `rpc_tests/` (Sondas de Comunicación con el Daemon)
Pruebas dinámicas contra el servidor local en ejecución:
- `test_daemons.py`: Escaneo de puertos en `daemon/hub_*.json` y comprobación de status HTTP.
- `read_hub61301.py`: Inspección del archivo de configuración del daemon activo.
- `test_rpc_calls.py`: Pruebas de invocación de endpoints (`GetConversationMetadata`, `GetCascadeTrajectory`).
- `test_rpc_markdown.py`: Prueba de generación directa de Markdown desde el daemon.
- `inspect_cascade_trajectory.py`: Análisis de los 15.000+ pasos devueltos por el endpoint.
- `inspect_steps_detail.py`: Mapeo de tipos de pasos (`USER_INPUT`, `PLANNER_RESPONSE`, etc.).
- `read_markdown_response.py`: Validación de la longitud y estructura del Markdown devuelto.
- `check_brain_steps.py`: Comparación entre los pasos en memoria y los archivos en `.system_generated/steps/`.
- `test_all_convs.py`: Prueba de estrés extrayendo las 30 conversaciones para verificar tasa de éxito (100%).
- `test_extractor.py`: Prototipo inicial del extractor completo antes de construir la CLI definitiva.


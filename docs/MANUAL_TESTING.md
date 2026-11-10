# Manual de Testing

Este documento reúne las pruebas manuales utilizadas para validar el comportamiento del exportador durante su modularización, verificando la estabilidad del CLI y de los componentes desacoplados tras cada iteración.

---

# v1.0.7 — Desacoplamiento de core/cli.py

## 1. Importación Aislada y Parser de Argumentos
Valida que `core/cli.py` construya y configure correctamente el `ArgumentParser` de la CLI.

**Comando:**
```powershell
python -c "from core.cli import build_parser, run_cli; print('CLI module import OK'); parser = build_parser(); print('Parser prog:', parser.prog)"
```

**Resultado:**
✔ `CLI module import OK`  
✔ `Parser prog: dump_antigravity.py` — Configuración limpia del parser.

---

## 2. Invocación de run_cli con Inyección de Argumentos en Memoria
Valida que `run_cli` acepte argumentos explícitos en lista sin depender de `sys.argv`.

**Comando:**
```powershell
python -c "from core.cli import run_cli; exit_code = run_cli(['--list']); print('Exit code:', exit_code)"
```

**Resultado:**
✔ Renderiza la tabla completa de sesiones y retorna `Exit code: 0`.

---

## 3. Ejecución End-to-End mediante el Runner Mínimo
Valida que `dump_antigravity.py` delegue en `core.cli.run_cli()` y conserve la funcionalidad idéntica.

**Comando:**
```powershell
python dump_antigravity.py --version
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ `dump_antigravity.py 1.0.6`  
✔ Extracción individual exitosa con feedback visual en terminal y código de salida `0`.

---

# v1.0.6 — Desacoplamiento de core/exporter.py

## 1. Importación Aislada del Motor Headless
Valida que `core/exporter.py` cargue sin dependencias de consola y exponga `export_conversation` y `export_all_conversations`.

**Comando:**
```powershell
python -c "from core.exporter import export_conversation, export_all_conversations; print('Exporter import OK')"
```

**Resultado:**
✔ `Exporter import OK` — Exportación correcta del orquestador headless.

---

## 2. Invocación Programática Headless (Modo SDK / Biblioteca)
Valida que `export_conversation` orqueste el flujo completo en memoria y devuelva el diccionario de rutas generadas sin emitir prints ni acoplarse a `sys.argv`.

**Comando:**
```powershell
python -c "from core.discovery import find_active_daemon; from core.client import AntigravityClient; from core.exporter import export_conversation; port, token = find_active_daemon(); client = AntigravityClient(port, token); paths = export_conversation(client, '1e706e7b-86d4-4155-898e-46000bc4baed'); print('Exported keys:', list(paths.keys()))"
```

**Resultado:**
✔ `Exported keys: ['raw', 'clean', 'markdown']` — Pipeline ejecutado y persistido de forma 100% programática.

---

## 3. Extracción End-to-End con CLI
Valida que `dump_antigravity.py` orqueste con `core/exporter.py` y reporte visualmente el progreso en la consola.

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ Conexión exitosa, feedback visual en consola y persistencia confirmada de los 3 formatos en `output/`.

---

# v1.0.5 — Desacoplamiento de core/writer.py

## 1. Importación Aislada y Sanitización de Rutas
Valida que `core/writer.py` cargue sin dependencias externas, sanitice caracteres reservados e inicialice las carpetas de salida de forma idempotente.

**Comando:**
```powershell
python -c "from core.writer import sanitize_filename, build_file_base, ensure_output_dirs; print('Writer import OK'); print('slug:', sanitize_filename('Hola: Mundo / Prueba?')); print('dirs:', list(ensure_output_dirs().keys()))"
```

**Resultado:**
✔ `Writer import OK`  
✔ `slug: Hola_Mundo__Prueba` — Sanitización cross-platform correcta.  
✔ `dirs: ['base', 'raw', 'clean', 'markdown']` — Creación idempotente y resolución de rutas.

---

## 2. Extracción End-to-End con Persistencia Modular
Valida que `dump_antigravity.py` orqueste `core/writer.py` para almacenar de forma atómica y consistente los 3 formatos en disco.

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ `[1/3] Raw JSON: 1e706e7b-86d4-4155-898e-46000bc4baed.raw.json`  
✔ `[2/3] Clean JSON: 2026-11-01_conversacion_1e706e7b.clean.json (3 msgs)`  
✔ `[3/3] Markdown: 2026-11-01_conversacion_1e706e7b.md (3081 chars)`  
Persistencia completa y verificada en `output/`.

---

# v1.0.4 — Desacoplamiento de core/client.py

## 1. Importación Aislada de core.client
Valida que el módulo de cliente cargue sin errores y exponga sus funciones y clase cliente.

**Comando:**
```powershell
python -c "from core.client import rpc_call, get_cascade_trajectory, convert_trajectory_to_markdown, AntigravityClient; print('Client import OK')"
```

**Resultado:**
✔ `Client import OK` — Exportación correcta de funciones y clase cliente.

---

## 2. Invocación RPC vía AntigravityClient
Valida que `AntigravityClient` mantenga estado de conexión y consulte exitosamente la trayectoria y la compilación a Markdown nativo.

**Comando:**
```powershell
python -c "from core.discovery import find_active_daemon; from core.client import AntigravityClient; port, token = find_active_daemon(); client = AntigravityClient(port, token); traj = client.get_trajectory('1e706e7b-86d4-4155-898e-46000bc4baed'); steps = traj.get('trajectory', {}).get('steps', []); traj_id = traj.get('trajectory', {}).get('trajectoryId'); md = client.to_markdown('1e706e7b-86d4-4155-898e-46000bc4baed', traj_id); print('Traj steps:', len(steps), 'MD chars:', len(md))"
```

**Resultado:**
✔ `Traj steps: 25 MD chars: 3081` — Invocación exitosa de `GetCascadeTrajectory` y `ConvertTrajectoryToMarkdown`.

---

## 3. Extracción End-to-End con CLI
Valida que `dump_antigravity.py` orqueste `core/client.py` para la extracción de la conversación y generación del triple archivo (`raw_json`, `clean_json`, `markdown`).

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ Conexión exitosa, 25 pasos recuperados y persistencia del triple formato (`.raw.json`, `.clean.json` y `.md`).

---

# v1.0.3 — Desacoplamiento de core/normalizer.py

## 1. Prueba Unitaria de Funciones Puras en Memoria
Valida que `core/normalizer.py` transforme marcas de tiempo y filtre turnos dialécticos sin efectos secundarios ni dependencias externas.

**Comando:**
```powershell
python -c "from core.normalizer import parse_iso_timestamp, extract_clean_messages; ts = parse_iso_timestamp('2026-11-01T14:30:00.123456Z'); mock_steps = [{'type': 'CORTEX_STEP_TYPE_USER_INPUT', 'userInput': {'userResponse': 'Hola'}, 'metadata': {'createdAt': '2026-11-01T14:30:00Z'}}, {'type': 'CORTEX_STEP_TYPE_PLANNER_RESPONSE', 'plannerResponse': {'response': 'Que tal'}, 'metadata': {'createdAt': '2026-11-01T14:30:05Z'}}]; msgs = extract_clean_messages(mock_steps); print('parse_iso:', ts); print('msgs count:', len(msgs)); print('roles:', [m['role'] for m in msgs])"
```

**Resultado:**
✔ `parse_iso: 1793554200`  
✔ `msgs count: 2`  
✔ `roles: ['user', 'assistant']` — Normalización correcta en memoria.

---

## 2. Extracción End-to-End con Generación de Clean JSON
Valida que `dump_antigravity.py` orqueste el normalizador y genere el archivo `.clean.json` con idéntica fidelidad.

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ Genera `2026-11-01_conversacion_1e706e7b.clean.json (3 msgs)` con esquema normalizado, IDs y timestamps limpios.

---

# v1.0.2 — Desacoplamiento de core/database.py

## 1. Importación Aislada de Base de Datos
Valida que `core/database.py` funcione de forma pura y autónoma sin depender del script orquestador.

**Comando:**
```powershell
python -c "from core.database import list_conversations; print('Convs:', len(list_conversations()))"
```

**Resultado:**
✔ `Isolated import OK, convs count: 30` — Conexión y consulta exitosas a `conversation_summaries.db`.

---

## 2. Listado de Catálogo desde la CLI
Valida que `dump_antigravity.py --list` consuma `core/database.py` y renderice la tabla completa.

**Comando:**
```powershell
python dump_antigravity.py --list
```

**Resultado:**
✔ Renderiza la tabla completa con las 30 conversaciones formateadas (ID, pasos, fecha y título).

---

## 3. Extracción con Resolución de Metadatos
Valida el ciclo completo: resolución de metadatos en SQLite vía `core/database.py`, descubrimiento de socket vía `core/discovery.py` y exportación triple.

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ Conecta al daemon activo, recupera 25 pasos y genera exitosamente los archivos en `raw_json`, `clean_json` y `markdown`.

---

# v1.0.1 — Desacoplamiento de core/discovery.py

## 1. Verificación de Versión CLI
Valida que el comando de versión funcione consumiendo la variable centralizada en el paquete `core`.

**Comando:**
```powershell
python dump_antigravity.py --version
```

**Resultado:**
✔ `dump_antigravity.py 1.0.1` — Versión expuesta correctamente.

---

## 2. Detección Dinámica de Daemon
Valida que el CLI localice el socket y token CSRF activo mediante `core/discovery.py`.

**Comando:**
```powershell
python dump_antigravity.py --id 1e706e7b
```

**Resultado:**
✔ `Conectado a Antigravity Daemon (puerto 60990)` — Localiza el descriptor `hub_*.json` y verifica el socket con `200 OK`.


# Manual de Testing

Este documento reúne las pruebas manuales utilizadas para validar el comportamiento del exportador durante su modularización, verificando la estabilidad del CLI y de los componentes desacoplados tras cada iteración.

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


# Plan: Extractor & Adaptador de Conversaciones Antigravity

**Objetivo:** Desarrollar una herramienta local y desacoplada que extraiga el historial completo de conversaciones almacenadas por Antigravity en formato binario (`.db` SQLite / `.pb`), lo convierta a JSON crudo estructurado y lo conecte con el pipeline de `chat-exporter` para generar Markdown.

**Directorio de trabajo:** `c:\xampp\htdocs\stock_productos\references\antygravity_adapter`

---

## Fases de Ejecución

### Fase 1: Descubrimiento e Inspección Estructural
* **Objetivo:** Analizar el esquema de las bases de datos de Antigravity sin modificar nada.
* **Tareas:**
  1. Inspeccionar `C:\Users\cochr\.gemini\antigravity\conversation_summaries.db` (tablas, campos, relación con IDs de conversación).
  2. Inspeccionar la carpeta `C:\Users\cochr\.gemini\antigravity\conversations\` y los archivos de sesión correspondientes a esta conversación (`1cfae999-9108-4b5e-955e-667dd3eeee89`).
  3. Mapear la estructura de almacenamiento de los turnos de diálogo (User vs Model, timestamps, y cómo se guardan las llamadas a herramientas vs texto final).

---

### Fase 2: Script Extractor a Raw JSON (`dump_antigravity.py`)
* **Objetivo:** Crear el puente binario ➡️ JSON.
* **Ubicación:** `references/antygravity_adapter/dump_antigravity.py`
* **Características del script:**
  - Cero dependencias externas (usa librería estándar de Python: `sqlite3`, `json`, `os`, `sys`).
  - Capaz de operar en dos modos:
    - **Modo individual:** `--id <conversation-id>` para extraer una conversación específica.
    - **Modo lote (Batch):** `--all` para listar y exportar todas las conversaciones del sistema.
  - Genera archivos JSON limpios con la estructura cruda:
    ```json
    {
      "id": "1cfae999-9108-4b5e-955e-667dd3eeee89",
      "title": "Título de la conversación",
      "created_at": "...",
      "messages": [
        { "id": "...", "role": "user", "text": "...", "timestamp": ... },
        { "id": "...", "role": "model", "text": "...", "timestamp": ... }
      ]
    }
    ```

---

### Fase 3: Validación del Historial Completo
* **Objetivo:** Comprobar que no haya pérdida de datos ni truncado.
* **Prueba de fuego:** Extraer la conversación actual (`1cfae999...`) y verificar que se recuperen íntegros los primeros pasos (febrero/marzo, génesis de *breadcrumbs*), confirmando que se esquiva el problema de compactación del IDE.

---

### Fase 4: Parser Adapter para `chat-exporter` (`antigravityParser.js`)
* **Objetivo:** Conectar el JSON al pipeline existente.
* **Ubicación:** `references/chat-exporter/antigravityParser.js` (siguiendo el patrón de tu `parser.js` de Joi).
* **Mapeo:**
  - `role`: `model` ➡️ `assistant`, `user` ➡️ `user`.
  - `timestamp`: normalización a segundos Unix.
  - `rawContent`: encapsulación para compatibilidad con el pipeline.
* **Salida:** Ejecución mediante la CLI existente para obtener el Markdown final (`.md`).

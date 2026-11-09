# Data Flow

## Objetivo

Este documento describe el recorrido que realizan los datos de una conversación desde su origen en el runtime de Antigravity hasta convertirse en los diferentes formatos de salida (`raw_json`, `clean_json`, `markdown`) y su posterior ingesta por parte del pipeline de `chat-exporter`.

Define el modelo conceptual de transformación, las etapas de refinamiento progresivo y los contratos de datos que conectan cada componente, sin entrar en detalles de implementación de bajo nivel.

---

## Visión general

El sistema opera como una tubería secuencial de desacoplamiento y enriquecimiento.

Cada etapa toma una representación de los datos con un formato específico y produce una nueva estructura con un mayor nivel de abstracción o utilidad semántica:

1. **Datos crudos en memoria:** Administrados por el proceso compilado de Antigravity.
2. **Transporte HTTP:** Paquetes JSON serializados transmitidos por ConnectRPC.
3. **Árbol de trayectoria (Fidelidad absoluta):** Estructura jerárquica con metadatos de ejecución, herramientas y respuestas.
4. **Mensajes dialécticos normalizados:** Diálogo lineal filtrado (Humano ↔ Asistente).
5. **Formatos finales:** Archivos inmutables en disco y streaming hacia pipelines externos.

---

## Flujo General del Sistema

```text
Language Server Daemon (Memoria viva de agy.exe)
        │
        ▼  [1. Discovery: hub_*.json]
Endpoint ConnectRPC (127.0.0.1:<puerto> + CSRF Token)
        │
        ▼  [2. RPC Call: GetCascadeTrajectory]
Trajectory RAW (Árbol completo de pasos y herramientas)
        │
        ├──────────────────────────────────────────┐
        ▼ [Persistencia directa]                   ▼ [3. Normalización]
output/raw_json/<id>.raw.json             extract_clean_messages()
                                                   │
        ┌──────────────────────────────────────────┤
        ▼ [4. RPC Call: Markdown]                  ▼ [Persistencia limpia]
ConvertTrajectoryToMarkdown               output/clean_json/<id>.clean.json
        │                                          │
        ▼                                          ▼ [5. Ingesta externa]
output/markdown/<id>.md                   chat-exporter (antigravityParser.js)
                                                   │
                                                   ▼
                                          chat-exporter Pipeline
                                          (filter → normalizer → markdown)
```

---

## Etapas del Flujo de Datos

### 1. Descubrimiento y Autenticación del Origen
* **Origen:** Sistema de archivos (`~/.gemini/antigravity/daemon/`).
* **Datos procesados:** Archivos descriptores `hub_<port>.json`.
* **Transformación:** Se inspeccionan los sockets disponibles y se valida la conectividad HTTP.
* **Salida de la etapa:**
  ```json
  {
    "port": 61301,
    "csrfToken": "6687a388-9286-4807-bbb4-73941ea280cc"
  }
  ```

---

### 2. Recuperación de Metadatos de Sesión (Catálogo)
* **Origen:** Base relacional `conversation_summaries.db`.
* **Datos procesados:** Tabla `conversation_summaries`.
* **Transformación:** Consulta SQL pasiva que mapea el identificador público (`conversation_id`) con su fecha de última modificación y título descriptivo.
* **Salida de la etapa:**
  ```text
  conversation_id: "13768fc6-3fb7-42fb-a498-d1532f97e39b"
  title: "Project Analysis And Review"
  last_modified: "2026-11-05"
  ```

---

### 3. Extracción de Trayectoria Cruda (GetCascadeTrajectory)
* **Petición saliente:**
  ```http
  POST /exa.language_server_pb.LanguageServerService/GetCascadeTrajectory
  Content-Type: application/json
  x-codeium-csrf-token: 6687a388-...

  { "cascadeId": "13768fc6-3fb7-42fb-a498-d1532f97e39b" }
  ```
* **Respuesta entrante:** Objeto `trajectory` con el grafo completo de pasos (`steps`), identificador interno (`trajectoryId`) y marcas de estado.
* **Destino A:** Escritura inmediata e inalterada en `output/raw_json/<id>.raw.json`.

---

### 4. Normalización Dialéctica y Poda de Ruido
* **Entrada:** Array polimórfico de `steps[]`.
* **Procesamiento:**
  * Se descartan pasos operativos que no corresponden a la interacción directa humano-máquina (`CORTEX_STEP_TYPE_EPHEMERAL_MESSAGE`, ejecuciones automáticas de comandos, lecturas intermedias de archivos, confirmaciones internas).
  * Se extrae el contenido textual genuino:
    * En pasos de usuario (`CORTEX_STEP_TYPE_USER_INPUT`): se extrae `userInput.userResponse` o se concatenan los ítems de texto en `userInput.items`.
    * En pasos de asistente (`CORTEX_STEP_TYPE_PLANNER_RESPONSE`): se extrae la respuesta visible `plannerResponse.response`.
  * Se normalizan las marcas temporales ISO 8601 a segundos Unix enteros (`timestamp`), eliminando fracciones de microsegundos que distorsionan el ordenamiento.
* **Destino B:** Escritura en `output/clean_json/<fecha>_<titulo>_<id>.clean.json`:
  ```json
  {
    "id": "13768fc6-3fb7-42fb-a498-d1532f97e39b",
    "trajectoryId": "d0554970-da44-493c-bfc1-a1bb4297f080",
    "title": "Project Analysis And Review",
    "messageCount": 30,
    "messages": [
      {
        "id": "c2711b67-9d12-...",
        "role": "user",
        "timestamp": 1793499329,
        "text": "Quiero que me digas que te parece qe es este proyecto..."
      },
      {
        "id": "bot-7af55e5b-...",
        "role": "assistant",
        "timestamp": 1793499351,
        "text": "Este proyecto es el repositorio de estudio..."
      }
    ]
  }
  ```

---

### 5. Compilación a Markdown Oficial (ConvertTrajectoryToMarkdown)
* **Petición saliente:**
  ```http
  POST /exa.language_server_pb.LanguageServerService/ConvertTrajectoryToMarkdown
  Content-Type: application/json
  x-codeium-csrf-token: 6687a388-...

  {
    "conversationId": "13768fc6-3fb7-42fb-a498-d1532f97e39b",
    "trajectoryId": "d0554970-da44-493c-bfc1-a1bb4297f080"
  }
  ```
* **Respuesta entrante:** Objeto `{ "markdown": "# Chat Conversation\n\n..." }`.
* **Destino C:** Escritura directa en `output/markdown/<fecha>_<titulo>_<id>.md`.

---

### 6. Ingesta Externa en `chat-exporter`
Cuando el usuario desea procesar la conversación a través del pipeline de `chat-exporter`:

```text
output/clean_json/
        │
        ▼
antigravityParser.js (extractMessages)
        │
        ▼  [Array de mensajes en modelo interno]
Core Pipeline (runPipeline)
        │
        ├─► filter.js (Filtro por rol: all | user | assistant)
        │
        ├─► normalizer.js (Empaquetado de texto y formato)
        │
        ├─► markdown.js (Formato de citas y timestamps humanos)
        │
        ▼
Markdown resultante de chat-exporter
```

* **Garantía arquitectónica:** El archivo `clean_json` actúa como el contrato de datos universal; `chat-exporter` no necesita saber que la conversación provino de una llamada ConnectRPC a un binario Go.


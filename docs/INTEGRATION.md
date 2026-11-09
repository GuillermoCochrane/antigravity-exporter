# Integración con `chat-exporter`

## Objetivo

Definir formalmente el contrato de integración que permite al proyecto `chat-exporter` procesar conversaciones originadas en Antigravity sin modificar su núcleo (`Core`), utilizando el patrón Adapter.

Este documento establece la especificación del esquema de datos intermedio (`clean_json`), la implementación del parser correspondiente y el procedimiento para ejecutar el pipeline de exportación.

---

## Filosofía de Integración

El núcleo de `chat-exporter` fue concebido para ser independiente del proveedor de origen (ChatGPT, Joi.ai, Claude, Gemini, Antigravity).

Para incorporar un nuevo proveedor sin violar el principio Open/Closed (abierto a extensión, cerrado a modificación), la integración sigue tres reglas:

1. **El Core no cambia:** Los módulos `filter.js`, `normalizer.js`, `markdown.js` y `writer.js` desconocen la existencia de Antigravity.
2. **Desacoplamiento de almacenamiento:** `chat-exporter` no interactúa con daemons ConnectRPC ni bases de datos SQLite; consume exclusivamente archivos JSON estructurados.
3. **Mapeo por Adapter:** La responsabilidad de traducir el esquema externo al modelo interno del pipeline recae exclusivamente en un módulo parser específico (`antigravityParser.js`).

---

## Arquitectura de Integración

```text
┌──────────────────────────────────────────────┐
│             antygravity_adapter              │
│                                              │
│  dump_antigravity.py                         │
│       │                                      │
│       ▼                                      │
│  output/clean_json/<archivo>.clean.json      │
└──────────────────────┬───────────────────────┘
                       │  (Contrato JSON)
                       ▼
┌──────────────────────────────────────────────┐
│                chat-exporter                 │
│                                              │
│  antigravityParser.js (Adapter)              │
│       │                                      │
│       ▼                                      │
│  Message[] (Modelo Interno del Pipeline)     │
│       │                                      │
│       ▼                                      │
│  Core Pipeline                               │
│  ┌────────────────────────────────────────┐  │
│  │ filter.js     (Filtrado por rol)       │  │
│  │ normalizer.js (Formato canónico)       │  │
│  │ markdown.js   (Citas y fechas)         │  │
│  └────────────────────────────────────────┘  │
│       │                                      │
│       ▼                                      │
│  Markdown final (.md)                        │
└──────────────────────────────────────────────┘
```

---

## Especificación del Contrato de Datos

### 1. Esquema de Entrada (`clean_json`)

Generado por `dump_antigravity.py` en la carpeta `output/clean_json/`. Representa el diálogo depurado de la conversación:

```json
{
  "id": "13768fc6-3fb7-42fb-a498-d1532f97e39b",
  "trajectoryId": "d0554970-da44-493c-bfc1-a1bb4297f080",
  "title": "Project Analysis And Review",
  "stepCount": 267,
  "messageCount": 30,
  "messages": [
    {
      "id": "c2711b67-9d12-455e-a607-e1ee462505c5",
      "role": "user",
      "timestamp": 1793499329,
      "text": "Quiero que me digas que te parece qe es este proyecto..."
    },
    {
      "id": "bot-7af55e5b-9851-4e0f-9add-439b5ed2ecc5",
      "role": "assistant",
      "timestamp": 1793499351,
      "text": "Este proyecto es el repositorio de estudio..."
    }
  ]
}
```

#### Campos requeridos en cada mensaje:
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `string \| null` | Identificador único del mensaje o turno. |
| `role` | `string` | Emisor del mensaje (`"user"` o `"assistant"`). |
| `timestamp` | `number \| null` | Marca temporal en segundos Unix (`epoch seconds`). |
| `text` | `string` | Contenido textual del mensaje. |

---

### 2. Modelo Interno Esperado por `chat-exporter`

El pipeline de `chat-exporter` requiere que cada elemento del array cumpla con la siguiente estructura:

```javascript
{
  id: string | null,
  parent: null,
  children: [],
  role: "user" | "assistant",
  createTime: number | null,   // Segundos Unix
  updateTime: null,
  status: "DONE",
  rawContent: {
    content_type: "text",
    parts: string[]            // [text]
  },
  metadata: {}
}
```

---

## Implementación del Adapter (`antigravityParser.js`)

**Ubicación:** `references/chat-exporter/antigravityParser.js`

El adaptador traduce de forma transparente el contrato `clean_json` al modelo interno:

```javascript
export function extractMessages(conversation) {
  const data = Array.isArray(conversation)
    ? (conversation[0]?.data ?? conversation[0])
    : conversation;
    
  const messagesList = data?.messages ?? (Array.isArray(conversation) ? conversation : []);

  const messages = [];

  for (const message of messagesList) {
    const role = message.role === "assistant" || message.role === "model" 
      ? "assistant" 
      : "user";
      
    const text = message.text ?? "";

    messages.push({
      id: message.id ?? null,
      parent: null,
      children: [],
      role,
      createTime: message.timestamp ?? null,
      updateTime: null,
      status: "DONE",
      rawContent: {
        content_type: "text",
        parts: text ? [text] : [],
      },
      metadata: {},
    });
  }

  return messages;
}
```

---

## Verificación de Integración

Se desarrolló el script de prueba `test_antigravity_pipeline.js` en la raíz de `chat-exporter` para validar la cadena completa de transformación:

```bash
node references/chat-exporter/test_antigravity_pipeline.js
```

### Salida de validación obtenida:
```text
Reading: references/antygravity_adapter/output/clean_json/2026-07-25_Analyzing_Breadcrumbs_Manager_Project_eacc4ff1.clean.json
Parsing Antigravity Clean JSON...
Extracted: 68 messages
Pipeline Markdown generated! Length: 237255 chars

--- Preview (first 25 lines) ---
## Usuario · 24/7/26, 11:08:20 p. m.

> Te animas a dedcuir que es este proyecto? Te tiro un tip, empeza por@[d:\programacion\proyectos\proyectos_menores\Breadcrumbs_manager\StockRa]...

## Asistente · 24/7/26, 11:08:20 p. m.

> ¡Dale, vamos a investigar! Empiezo por donde me decís y después reviso todo el proyecto.
```

### Resultados de la prueba:
- **Integridad:** 68 mensajes procesados sin pérdidas ni excepciones.
- **Formateo:** Aplicación exitosa del formateador de roles, fechas humanas en formato local y bloques de cita Markdown (`> `).
- **Compatibilidad:** 100% intercambiable con las fuentes de ChatGPT y Joi.ai.


# REGLAS PERSISTENTES DEL PROYECTO (Antigravity Identity)

> [!IMPORTANT]
> Estas instrucciones son de cumplimiento OBLIGATORIO para el asistente de IA en cada nueva sesión de este proyecto. No deben ser ignoradas ni eliminadas.

## 1. Protocolo de Inicio de Sesión (Must-Have)

- **Acción Obligatoria:** Al iniciar cualquier nueva tarea o conversación desde cero, lo primero que debe hacer el agente es leer el **Orquestador de Breadcrumbs**:
  - **Ruta:** [readme.md](file:///c:/xampp/htdocs/stock_productos/references/mds/breadcrumbs/readme.md)
- **Propósito:** El `readme.md` actúa como el índice central de la memoria del proyecto. El agente debe seguir sus instrucciones y revisar los archivos que allí se indiquen (`USER_PROFILE.md`, `project_state.md`, `architecture_decisions.md`, etc.) para entender el contexto actual, las preferencias del usuario y las convenciones establecidas.

## 2. Gestión de Reportes y Breadcrumbs

- **Coherencia Sintáctica:** Antes de redactar cualquier nuevo reporte de PR en `references/mds/pr/`, el agente debe leer obligatoriamente los reportes previos para asegurar que el estilo, la estructura y la terminología sean totalmente coherentes con lo ya establecido.
- Al completar un cambio significativo y cerrar una sesión, el agente debe:
  1. Leer reportes previos en la carpeta designada para empatar estilo.
  2. Escribir la descripción de la nueva PR en `references/mds/pr/`.
  3. Actualizar el estado del proyecto en `references/mds/breadcrumbs/project_state.md`.
  4. Actualizar las tareas (tickets/QA) en `references/mds/breadcrumbs/reporte.md`.

## 3. Control de Proactividad (Autorización Obligatoria)

- **Permiso Primero:** El agente debe ser menos proactivo de manera autónoma. No debe ejecutar cambios de código, instalaciones o modificaciones estructurales sin haber recibido una autorización explícita previa del usuario.
- **Flujo Sugerido:** Detectar problema -> Plantear solución -> Pedir autorización -> Ejecutar tras el "OK".

---

## 4. Memoria Proactiva (Gestión Autónoma de Breadcrumbs)

- **El asistente tiene la autoridad y el deber** de actualizar autónomamente *cualquier* archivo dentro de la carpeta `references/mds/breadcrumbs/` o su propio `USER_PROFILE.md` cuando considere que ha aprendido algo nuevo sobre el sistema.
- **¿Cuándo hacerlo?** Al cierre de un ticket, sesión de trabajo, o cuando descubra:
  - Nuevos patrones de diseño acordados.
  - Reglas de negocio no documentadas que limitan el sistema.
  - Preferencias de código del usuario.
- **Filosofía del Usuario:** Las breadcrumbs son "la memoria de la IA". El usuario no las modifica; dependen del agente para mantenerse vivas y útiles.

---

## 5. Patrón de Modularización del "Tanque" (Arquitectura de Referencia)

El agente debe seguir este flujo descendente para cada refactorización de un módulo monolítico:

1.  **Separación por Responsabilidades**: Aislar lógica (`*_logic.php`), scripts (`*_script.php`) y estilos del template principal.
2.  **Seccionamiento**: Dividir el template en grandes bloques funcionales dentro de `views/partials/{feature}/`.
3.  **Atomización**: Dentro de subcarpetas nombradas según la sección (ej: `partials/{feature}/{seccion}/`), fragmentar en archivos más pequeños, priorizando etiquetas semánticas (ej: `<article>`) sobre `divs`.
4.  **Componentización**: Si un elemento se repite en distintas secciones o módulos, moverlo a la carpeta global `views/components/`.

## 6. Regla de Oro de Consistencia Workflow (Must-Check)

> [!IMPORTANT]
> **Antes de iniciar cualquier nuevo refactor o modularización**, el agente debe revisar obligatoriamente los refactors previos exitosos (especialmente el patrón **"Smart Manager -> Dumb Template"** de la sección de Ventas y Scanner). No se debe improvisar un patrón nuevo si ya existe uno consolidado para el mismo propósito, asegurando la coherencia técnica de todo el sistema.

---

## 7. Metodología de Sprints y Planificación Estricta (Workflow)

Para evitar la "visión de túnel" y mantener una escalabilidad de nivel Enterprise, el agente debe respetar el siguiente ciclo de vida (Sprint Workflow) en todo feature grande:

1. **Fase de Planificación (`references/mds/breadcrumbs/planificaction/`):**
   - Antes de escribir código, el scope debe estar documentado en un `walkthrough.md` maestro y sus respectivos `implementation_plan_*.md`.
   - Estos archivos definen la arquitectura, fases secuenciales y criterios de aceptación.
2. **Fase de Ejecución Guiada:**
   - El agente usará los planes como blueprint, evitando desviarse hacia tareas no contempladas que engorden el scope.
3. **Fase de Cierre (Reporte PR Integral):**
   - Al finalizar, el PR redactado en `references/mds/pr/` **NO debe limitarse a la última tarea realizada**. Debe ser un documento profundo y exhaustivo que resuma **todo el trabajo del sprint completo** basándose en el `walkthrough.md` y todos los `implemenatation_plans_*.md`.
   - Debe incluir: Contexto, Análisis Comparativo (tablas), Decisiones Arquitectónicas y Métricas de Impacto (reducción de deuda técnica).
4. **Fase de Actualización de Trackers (Clausura):**
   - Finalmente, se registra el nombre del nuevo PR en `project_state.md` y se actualiza el estado de las tareas en `reporte.md`.

---

## 8. Herramienta de busqueda

Tratar de evitar el uso de la herramienta interna de busqueda, ya que la misma entra en un loop infinito y bloquea la ejecucion del flujo de trabajo

*Este artefacto sirve como ancla de identidad para que el agente no pierda el "hilo conductor" del desarrollo a través de múltiples historiales.*


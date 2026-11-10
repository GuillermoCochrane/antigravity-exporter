# Implementation Plan: Consolidación y Release v1.1.0 (Paso 8)

## 1. Objetivo y Alcance

Cerrar, consolidar y publicar formalmente el **Sprint 01: Modularización y Desacoplamiento**, culminando en la **Release Menor v1.1.0**.

Este paso final certifica que:
1. El script original monolítico de 239 líneas ha sido transformado en una **Arquitectura Hexagonal desacoplada en capas**:
   - `dump_antigravity.py`: Runner ejecutable mínimo (11 líneas).
   - `core/discovery.py`: Capa 2 (Descubrimiento y sondeo HTTP del socket activo y token CSRF).
   - `core/database.py`: Capa 1 (Catálogo y consultas SQLite sobre `conversation_summaries.db`).
   - `core/client.py`: Capa 3 (Transporte ConnectRPC sobre HTTP, llamadas `GetCascadeTrajectory` y `ConvertTrajectoryToMarkdown`, y cliente `AntigravityClient`).
   - `core/normalizer.py`: Capa 4 (Funciones 100% puras de normalización dialéctica y parseo de marcas de tiempo).
   - `core/writer.py`: Capa 5 (Gestión de rutas, sanitización cross-platform de nombres y persistencia atómica en `utf-8`).
   - `core/exporter.py`: Capa 6 (Orquestación del motor headless / pipeline de caso de uso).
   - `core/cli.py`: Capa de Presentación (Adaptador CLI con soporte para pruebas en memoria y renderizado de consola).
2. Se ejecuta la suite completa de pruebas de regresión para garantizar 100% de retrocompatibilidad.
3. Se actualiza la memoria técnica y pública del proyecto (`README.md`, `ROADMAP.md`, `CHANGELOG.md`, `MANUAL_TESTING.md`).
4. Se crea el tag anotado Git `v1.1.0` y se sincroniza con el repositorio remoto en GitHub.

---

## 2. Documentación Pública y Cierre de Fase

1. **`README.md`:**
   - Actualizar badge a `v1.1.0`.
   - Estado del proyecto reflejando las 6 capas modulares de `core/`.
   - Renovación del árbol de directorios del proyecto.
2. **`docs/ROADMAP.md`:**
   - Marcar la **Fase 2 (Sprint 01: Modularización)** como 100% completada.
   - Activar la **Fase 3 (Sprint 02: Batería de Pruebas Automatizadas y Fixtures, v1.2.0)** como próximo hito inmediato.
3. **`docs/CHANGELOG.md`:**
   - Incorporar la cabecera consolidada de la versión `v1.1.0` resumiendo la evolución arquitectónica completa del sprint.
4. **`docs/MANUAL_TESTING.md`:**
   - Asentar la suite completa de regresión de release `v1.1.0`.
5. **`planification/01-modularizacion/walkthrough.md`:**
   - Marcar el Paso 8 como completado (`[x]`).
   - Validar y marcar todos los Criterios de Aceptación del Sprint (`[x]`).

---

## 3. Checklist de Verificación Manual (Suite Completa de Regresión)

- [ ] `python dump_antigravity.py --version` -> Retorna versión `1.1.0` consumida desde `core.__version__`.
- [ ] `python dump_antigravity.py --help` -> Muestra el menú de ayuda sin errores de sintaxis.
- [ ] `python dump_antigravity.py --list` -> Renderiza la tabla completa de 30 conversaciones.
- [ ] `python dump_antigravity.py --id 1e706e7b` -> Exporta quirúrgicamente una conversación y genera los 3 formatos en `output/`.
- [ ] Validar que los 3 archivos en `output/` mantengan idéntica fidelidad a los generados en la versión v1.0.0.

---

## 4. Secuencia de Commits y Release (v1.1.0)

Siguiendo la especificación de [`planification/rules/COMMIT_TEMPLATES.md`](../rules/COMMIT_TEMPLATES.md):

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de implementacion para release v1.1.0
   ```
2. **Documentación Global (README, Roadmap, Changelog, Manual Testing):**
   ```text
   docs: actualizar README, roadmap y changelog consolidado para v1.1.0
   ```
3. **Bump de Versión (Release):**
   ```text
   chore: actualizar version a 1.1.0
   ```
4. **Git Tag y Push:**
   ```powershell
   git tag -a v1.1.0 -m "Release v1.1.0: Modularización completa del extractor y arquitectura hexagonal"
   git push origin main --tags
   ```


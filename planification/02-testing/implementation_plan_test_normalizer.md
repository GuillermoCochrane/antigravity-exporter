# Implementation Plan: Tests Unitarios y Fixtures para Módulo Normalizer (v1.1.1)

## 1. Objetivo y Alcance

Implementar el primer conjunto de pruebas automatizadas y fixtures sintéticos en la suite `tests/`, enfocado exclusivamente en **`core/normalizer.py`**.

Al ser `normalizer.py` una colección de **funciones 100% puras** (cero I/O de disco, red o base de datos), este hito establece:
1. La estructura base del directorio `tests/` y `tests/fixtures/`.
2. Las pruebas unitarias directas para el parsing de fechas ISO y la extracción dialéctica.
3. Fixtures sintéticos reproducibles que garantizan retrocompatibilidad con la extensión `chat-exporter`.
4. El patrón estándar para correr pruebas usando `unittest` nativo de Python.

---

## 2. Estructura de Archivos a Crear

```text
antigravity-exporter/
├── tests/
│   ├── __init__.py                               # Declara el paquete de testing
│   ├── fixtures/
│   │   ├── sample_trajectory.json                # Fixture sintético de ConnectRPC
│   │   └── expected_normalized.json              # Salida esperada para chat-exporter
│   └── test_normalizer.py                        # Suite TestCase para core.normalizer
└── planification/
    └── 02-testing/
        └── implementation_plan_test_normalizer.md # Este documento
```

---

## 3. Casos de Prueba a Implementar (`TestNormalizer`)

### 1. `test_parse_iso_timestamp`
- **Valores válidos:**
  - Formato ISO estándar con sufijo `Z`: `'2026-11-01T14:30:00Z'` ➔ Retorna epoch entero `1793543400` (o equivalente local).
  - Formato ISO con microsegundos y `Z`: `'2026-11-01T14:30:00.123456Z'` ➔ Retorna epoch entero.
- **Casos de borde y valores inválidos:**
  - `None` ➔ Retorna `None`.
  - Cadena vacía `""` ➔ Retorna `None`.
  - Cadena malformada o no parseable (`"no-una-fecha"`, `12345`) ➔ Retorna `None` sin lanzar excepciones.

### 2. `test_extract_clean_messages`
- **Filtrado dialéctico:**
  - Debe extraer pasos de usuario (`CORTEX_STEP_TYPE_USER_INPUT`) vía `userResponse`.
  - Debe extraer pasos de usuario alternativos vía `items` con campo `text`.
  - Debe extraer respuestas del asistente (`CORTEX_STEP_TYPE_PLANNER_RESPONSE`) vía `response`.
  - Debe ignorar pasos de telemetría interna: tool calls (`CORTEX_STEP_TYPE_TOOL_CALL`), pensamientos (`thought`), telemetría de sistema.
- **Resiliencia ante contenido vacío:**
  - Pasos con `userResponse` vacío o compuesto solo por espacios en blanco no deben agregarse a la lista.
  - Pasos con `response` de modelo vacío o solo espacios no deben agregarse.
- **Identificadores de mensaje (Fallback IDs):**
  - Si el paso de usuario no tiene `executionId`, debe asignar el fallback secuencial `user_0`, `user_1`, etc.
  - Si el paso del modelo no tiene `messageId`, debe asignar el fallback secuencial `bot_0`, `bot_1`, etc.

### 3. `test_build_clean_conversation`
- Valida la estructura de diccionario de alto nivel para consumo de `chat-exporter`:
  - Claves requeridas presentes: `id`, `trajectoryId`, `title`, `stepCount`, `messageCount`, `messages`.
  - Coherencia numérica: `stepCount == len(raw_steps)` y `messageCount == len(messages)`.

### 4. `test_fixture_regression`
- Carga `sample_trajectory.json` desde disco y lo normaliza con `build_clean_conversation`.
- Compara el resultado contra `expected_normalized.json` para garantizar fidelidad del 100% ante regresiones futuras.

---

## 4. Diseño de Fixtures Sintéticos (`tests/fixtures/`)

### `sample_trajectory.json`
Un archivo JSON sintético y autocontenido que modela un ciclo conversacional completo:
1. Paso 1: Usuario (`userResponse`: `"Hola, ayudame a escribir un test."`).
2. Paso 2: Telemetría / Tool Call (debe ser filtrado y omitido).
3. Paso 3: Pensamiento interno / Thought (debe ser filtrado y omitido).
4. Paso 4: Asistente (`response`: `"¡Por supuesto! Acá tenés la solución."`).
5. Paso 5: Usuario con formato alternativo (`items`: `[{"text": "Muchas gracias!"}]`).
6. Paso 6: Paso vacío o malformado (para validar robustez).

---

## 5. Checklist de Verificación

- [ ] `tests/__init__.py` creado.
- [ ] `tests/fixtures/sample_trajectory.json` y `expected_normalized.json` creados y válidos sintácticamente.
- [ ] `tests/test_normalizer.py` implementado con clase `unittest.TestCase`.
- [ ] Ejecución manual de test unitario:
  ```powershell
  python -m unittest tests/test_normalizer.py -v
  ```
- [ ] Todos los tests pasan en verde (0 fallos, 0 errores) en < 100 ms.
- [ ] Ejecución mediante discovery general:
  ```powershell
  python -m unittest discover tests -v
  ```

---

## 6. Secuencia de Commits (Micro-Sprint v1.1.1)

Siguiendo `planification/rules/COMMIT_TEMPLATES.md`:

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de tests y fixtures para modulo normalizer
   ```
2. **Implementación de Tests:**
   ```text
   test(normalizer): implementar tests unitarios y fixtures para core/normalizer
   ```
3. **Documentación:**
   ```text
   docs(normalizer): documentar suite de tests en manual_testing y changelog v1.1.1
   ```
4. **Bump de Versión:**
   ```text
   chore: actualizar version a 1.1.1
   ```


# Walkthrough: Sprint 02 — Batería de Pruebas Automatizadas y Fixtures (v1.2.0)

## 1. Contexto y Objetivo

En el **Sprint 01 (`v1.1.0`)**, logramos la modularización total de `dump_antigravity.py`, desacoplando responsabilidades en 7 módulos independientes dentro de `core/` con una arquitectura hexagonal limpia y testeable.

El objetivo de este **Sprint 02 (`v1.2.0`)** es construir una **suite integral de pruebas automatizadas y fixtures reproducibles** que blinde el comportamiento del extractor ante futuras modificaciones, actualizaciones del daemon de Antigravity o ampliaciones de formato.

### Principios Fundamentales del Sprint:
1. **Regla de Oro: Cero Dependencias Externas:** Se utilizará exclusivamente la biblioteca estándar de Python (`unittest`, `unittest.mock`, `tempfile`, `sqlite3`, `io`, `json`). Cero `pip install pytest`.
2. **Ejecución Instantánea (< 2 segundos):** Todas las pruebas deben correr en milisegundos en cualquier entorno (Windows, macOS, Linux, CI/CD) sin necesidad de configurar servicios ni entornos virtuales.
3. **Aislamiento Hermético (Zero Side-Effects):**
   - Ninguna prueba debe realizar llamadas de red reales ni requerir que Antigravity esté abierto.
   - Ninguna prueba debe leer o modificar la base de datos SQLite de producción del usuario.
   - Ninguna prueba debe escribir en el directorio `output/` real (uso estricto de `tempfile.TemporaryDirectory`).
4. **Metodología Tetrad:** Cada módulo mantendrá el ciclo estricto de 4 pasos (`docs(planification)`, `test`, `docs`, `chore`).

---

## 2. Arquitectura de la Suite de Pruebas (`tests/`)

```text
antigravity-exporter/
├── dump_antigravity.py          # Runner de producción
├── core/                        # Los 7 módulos desacoplados
│   ├── discovery.py
│   ├── database.py
│   ├── client.py
│   ├── normalizer.py
│   ├── writer.py
│   ├── exporter.py
│   └── cli.py
├── tests/                       # Suite de pruebas automatizadas
│   ├── __init__.py
│   ├── fixtures/                # Muestras sintéticas y anonimizadas de datos
│   │   ├── raw_rpc_trajectory.json       # Payload representativo de ConnectRPC
│   │   ├── expected_normalized.json      # Salida esperada compatible con chat-exporter
│   │   └── fake_hub.json                 # Descriptor simulado de socket/token CSRF
│   ├── test_normalizer.py       # 1. Transformación pura de mensajes (cero I/O)
│   ├── test_database.py         # 2. Consultas SQLite aisladas en memoria (:memory:)
│   ├── test_writer.py           # 3. Persistencia atómica y rutas en directorios temporales
│   ├── test_discovery.py        # 4. Parseo de descriptores hub_*.json y simulación de socket
│   ├── test_client.py           # 5. Cliente ConnectRPC y headers simulando urllib.request
│   ├── test_cli.py              # 6. Parseo de flags CLI y renderizado de consola en memoria
│   ├── test_exporter.py         # 7. Test de integración del pipeline completo headless
│   └── run_tests.py             # Runner directo centralizado
└── planification/
    └── 02-testing/              # Planes detallados de cada micro-sprint
```

---

## 3. Matriz de Cobertura y Estrategia por Módulo

| Módulo en `core/` | Archivo de Test | Estrategia de Prueba | Dependencia Simulada |
|---|---|---|---|
| `core/normalizer.py` | `tests/test_normalizer.py` | Prueba pura con fixtures JSON de entrada/salida. | Ninguna (función 100% matemática en memoria). |
| `core/database.py` | `tests/test_database.py` | Creación de schema en SQLite `:memory:` y consultas. | Base SQLite volátil en memoria. |
| `core/writer.py` | `tests/test_writer.py` | Creación y borrado atómico con `tempfile`. | Disco temporal aislado del SO. |
| `core/discovery.py` | `tests/test_discovery.py` | Mocks de `%APPDATA%`, JSON de hub y sockets. | `os.walk`, `socket.socket`. |
| `core/client.py` | `tests/test_client.py` | Mocking de `urllib.request.urlopen` y errores HTTP. | Red simulada con `unittest.mock`. |
| `core/cli.py` | `tests/test_cli.py` | Invocación de `run_cli(args_list)` y captura de `stdout`. | `sys.stdout` con `io.StringIO`. |
| `core/exporter.py` | `tests/test_exporter.py` | Integración headless de punta a punta con mocks de red. | Orquestador completo mockeando el cliente. |

---

## 4. Fases del Sprint y Tracker de Progreso

| Estado | Paso | Versión | Archivo de Prueba | Plan de Implementación | Responsabilidad Principal |
|:---:|:---:|:---:|---|---|---|
| [ ] | **1** | `1.1.1` | `test_normalizer.py` + Fixtures | [`implementation_plan_test_normalizer.md`](implementation_plan_test_normalizer.md) | Fixtures sintéticos y test de filtrado dialéctico |
| [ ] | **2** | `1.1.2` | `test_database.py` | [`implementation_plan_test_database.md`](implementation_plan_test_database.md) | Queries SQLite en `:memory:` y helpers de catálogo |
| [ ] | **3** | `1.1.3` | `test_writer.py` | [`implementation_plan_test_writer.md`](implementation_plan_test_writer.md) | Escritura atómica, sanitización de paths y UTF-8 |
| [ ] | **4** | `1.1.4` | `test_discovery.py` | [`implementation_plan_test_discovery.md`](implementation_plan_test_discovery.md) | Parseo de descriptores hub y mock de socket vivo |
| [ ] | **5** | `1.1.5` | `test_client.py` | [`implementation_plan_test_client.md`](implementation_plan_test_client.md) | Mock de ConnectRPC, headers CSRF y manejo de errores HTTP |
| [ ] | **6** | `1.1.6` | `test_cli.py` | [`implementation_plan_test_cli.md`](implementation_plan_test_cli.md) | CLI en memoria con `args_list` y captura de `stdout` |
| [ ] | **7** | `1.1.7` | `test_exporter.py` + `run_tests.py` | [`implementation_plan_test_exporter.md`](implementation_plan_test_exporter.md) | Integración headless end-to-end y runner global |
| [ ] | **8** | `v1.2.0` | Release Menor | [`implementation_plan_release.md`](implementation_plan_release.md) | Suite completa en verde, docs globales y release tag |

---

## 5. Criterios de Aceptación del Sprint

- [ ] Todos los tests se ejecutan con éxito mediante `python -m unittest discover tests` y `python tests/run_tests.py`.
- [ ] Tiempo total de ejecución inferior a 2 segundos en máquina local.
- [ ] 100% estándar de Python (cero bibliotecas de terceros en `requirements.txt`).
- [ ] Cero interacción con el daemon de Antigravity o puertos locales abiertos durante los tests.
- [ ] Cero escrituras accidentales en la base de datos real o en la carpeta `output/` del proyecto.
- [ ] Al finalizar el paso 8, se actualizan `docs/CHANGELOG.md`, `docs/ROADMAP.md` y `README.md` formalizando la entrega de `v1.2.0`.


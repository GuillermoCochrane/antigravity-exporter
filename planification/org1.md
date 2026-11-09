Created organize_workspace.py
Ran organize lab files into categorized folders
Ran verify root folder cleanup
Ran move remaining find scripts to lab
Created README.md
Ran verify dump_antigravity help

¡Excelente! Ya quedó **todo perfectamente organizado por responsabilidades**, con cero archivos eliminados y con una estructura espejo a la filosofía que aplicaste en `chat-exporter`.

Así quedó la arquitectura limpia de `references/antygravity_adapter/`:

```text
antygravity_adapter/
│
├── README.md                # Documentación general de uso de la herramienta
├── dump_antigravity.py      # La CLI principal de exportación (producción)
│
├── planification/           # Documentación y reglas de trabajo
│   ├── plan_antigravity_adapter.md
│   ├── project_rules.md
│   ├── walkthrough_movs.md
│   └── implementation_plan_movs.md
│
├── output/                  # Las exportaciones generadas
│   ├── raw_json/            # Árbol JSON íntegro con cada detalle de la API
│   ├── clean_json/          # Mensajes normalizados para tu pipeline de chat-exporter
│   └── markdown/            # Markdown oficial renderizado por Antigravity
│
└── lab/                     # El laboratorio de sondas e ingeniería inversa (con su propio README)
    ├── README.md            # Índice que explica para qué sirve cada sonda
    ├── database/            # 7 scripts de inspección de SQLite, schemas y FTS5
    ├── encoding/            # 6 scripts de análisis de compresión, binarios y .pb
    ├── rpc_discovery/       # 17 scripts de rastreo y desensamblado de endpoints ConnectRPC
    └── rpc_tests/           # 10 scripts de pruebas dinámicas contra el daemon
```

### Lo que se logró:
1. **Raíz impecable:** En la raíz solo tenés la herramienta ejecutable (`dump_antigravity.py`), su `README.md` y las carpetas de responsabilidad.
2. **Historial de investigación preservado:** Los 40 scripts auxiliares que usamos para descubrir la arquitectura están intactos y clasificados en `lab/` con un `README.md` explicativo por si algún día querés repasar o enseñar cómo se descubrió cada parte.
3. **Planes resguardados:** Toda la planificación sigue disponible en `planification/`.
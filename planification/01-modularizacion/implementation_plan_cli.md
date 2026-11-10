# Implementation Plan: Módulo CLI (v1.0.7)

## 1. Objetivo y Alcance

Extraer la capa de presentación de terminal, parsing de argumentos y formateo visual (Presentation Layer / CLI Adapter) desde `dump_antigravity.py` hacia un módulo dedicado: **`core/cli.py`**.

Este módulo actúa como el **adaptador de consola** del sistema:
1. Configura el analizador de argumentos de línea de comandos mediante `argparse`.
2. Permite inyección de argumentos opcional (`args_list: list[str] = None`) en lugar de acoplarse rígidamente a `sys.argv`, habilitando tests unitarios directos sin simulación de procesos.
3. Formatea y renderiza la tabla visual de conversaciones para el modo `--list`.
4. Coordina la interacción con el usuario en terminal para exportaciones individuales (`--id`) y por lotes (`--all`), reportando el estado visual de cada artefacto persistido.
5. Retorna códigos de salida enteros (`0` para éxito, `1` para error) conformes al estándar POSIX/Windows.

---

## 2. Contratos de Entrada y Salida (API del Módulo)

### 1. `build_parser`
```python
def build_parser() -> argparse.ArgumentParser:
    """
    Construye y configura el parser de argumentos de la herramienta con su descripción,
    versión dinámica y flags (--version, --list, --id, --all).
    """
```

### 2. `print_conversations_table`
```python
def print_conversations_table(convs: list[tuple]) -> None:
    """
    Imprime en terminal la tabla formateada del catálogo de sesiones históricas
    (columnas: ID, PASOS, FECHA, TITULO / PREVIEW).
    """
```

### 3. `run_cli` (Entrypoint principal del CLI)
```python
def run_cli(args_list: list[str] = None) -> int:
    """
    Ejecuta el ciclo de vida del comando CLI.
    
    Args:
        args_list (list[str], optional): Lista de argumentos explícita (ej: ['--id', '1e706e7b']).
                                         Si es None, parsea sys.argv[1:].
                                         
    Returns:
        int: Código de salida del proceso (0: OK, 1: Error o aborto).
    """
```

---

## 3. Código Afectado en `dump_antigravity.py`

* **Transformación de `dump_antigravity.py`:**
  Pasa a ser un ejecutable ultra-liviano de 10 líneas, cuya única función es importar `run_cli` y pasarlo a `sys.exit()`:
  ```python
  #!/usr/bin/env python3
  import sys
  from core.cli import run_cli

  if __name__ == "__main__":
      sys.exit(run_cli())
  ```

---

## 4. Archivos a Crear / Modificar

1. **`planification/01-modularizacion/implementation_plan_cli.md` (Nuevo):**
   * Especificación técnica del módulo adaptador CLI.
2. **`core/cli.py` (Nuevo):**
   * Implementación de `build_parser`, `print_conversations_table` y `run_cli`.
   * Cero dependencias externas (`os`, `sys`, `argparse`).
3. **`dump_antigravity.py` (Modificado):**
   * Reducido a runner delegador mínimo.

---

## 5. Checklist de Verificación Manual

- [x] Importar `core.cli` de forma aislada y validar `build_parser()`.
- [x] Ejecutar `run_cli(["--version"])` y `run_cli(["--help"])` pasando listas en memoria y verificar código de salida `0`.
- [x] Ejecutar `python dump_antigravity.py --list` y verificar renderizado de tabla.
- [x] Ejecutar `python dump_antigravity.py --id 1e706e7b` y verificar flujo completo con código de salida `0`.

---

## 6. Tríada de Commits para v1.0.7

1. **Planificación:**
   ```text
   docs(planification): incorporar plan de implementacion para modulo cli
   ```
2. **Refactor (Código):**
   ```text
   refactor(cli): desacoplar adaptador de consola a core/cli
   ```
3. **Docs (Documentación):**
   ```text
   docs(cli): documentar modulo core/cli, manual_testing y changelog v1.0.7
   ```
4. **Chore (Versión):**
   ```text
   chore: actualizar version a 1.0.7
   ```


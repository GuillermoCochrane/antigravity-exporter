#!/usr/bin/env python3
"""
Antigravity Conversation Exporter (Entrypoint)
Lanzador mínimo de la herramienta CLI.
"""

import sys
from core.cli import run_cli

if __name__ == "__main__":
    sys.exit(run_cli())

import sqlite3
import os
import sys

BASE_DIR = r"C:\Users\cochr\.gemini\antigravity"
SUMMARIES_DB = os.path.join(BASE_DIR, "conversation_summaries.db")
CONVERSATIONS_DIR = os.path.join(BASE_DIR, "conversations")

print(f"--- 1. Inspeccionando {SUMMARIES_DB} ---")
if os.path.exists(SUMMARIES_DB):
    try:
        conn = sqlite3.connect(SUMMARIES_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tablas encontradas ({len(tables)}):")
        for table_name, sql in tables:
            print(f"\n[Tabla: {table_name}]")
            print(f"SQL: {sql}")
            try:
                cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
                count = cursor.fetchone()[0]
                print(f"Total filas: {count}")
                cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT 2")
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                print(f"Columnas: {col_names}")
                for r in rows:
                    print(f"  Fila muestra: {r}")
            except Exception as e:
                print(f"  Error leyendo tabla {table_name}: {e}")
        conn.close()
    except Exception as e:
        print(f"Error conectando a summaries.db: {e}")
else:
    print("No se encontro conversation_summaries.db")

print(f"\n--- 2. Inspeccionando carpeta de conversaciones: {CONVERSATIONS_DIR} ---")
if os.path.exists(CONVERSATIONS_DIR):
    try:
        items = os.listdir(CONVERSATIONS_DIR)
        print(f"Total elementos en conversations: {len(items)}")
        for item in items[:20]:
            item_path = os.path.join(CONVERSATIONS_DIR, item)
            size = os.path.getsize(item_path) if os.path.isfile(item_path) else "DIR"
            print(f"  {item} ({size})")
    except Exception as e:
        print(f"Error listando {CONVERSATIONS_DIR}: {e}")
else:
    print(f"No existe o no es accesible: {CONVERSATIONS_DIR}")


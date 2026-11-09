import sqlite3
import os

VSCDB_PATH = os.path.expandvars(r"%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb")
print("VSCDB path:", VSCDB_PATH)

if os.path.exists(VSCDB_PATH):
    conn = sqlite3.connect(VSCDB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for t, _ in tables:
        cursor.execute(f"SELECT COUNT(*) FROM \"{t}\"")
        print(f"Table {t} count: {cursor.fetchone()[0]}")
        cursor.execute(f"SELECT [key] FROM \"{t}\" WHERE [key] LIKE '%1cfae999%' OR [key] LIKE '%conversation%' LIMIT 10")
        print("Matching keys:", cursor.fetchall())
    conn.close()


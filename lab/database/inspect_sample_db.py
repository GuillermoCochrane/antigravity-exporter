import sqlite3
import os

BASE_DIR = r"C:\Users\cochr\.gemini\antigravity\conversations"
sample_db = os.path.join(BASE_DIR, "13768fc6-3fb7-42fb-a498-d1532f97e39b.db")

print(f"--- Inspeccionando {sample_db} ---")
conn = sqlite3.connect(sample_db)
cursor = conn.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
for t, sql in cursor.fetchall():
    print(f"\nTabla: {t}")
    print(f"SQL: {sql}")
    cursor.execute(f"SELECT COUNT(*) FROM \"{t}\"")
    print(f"Count: {cursor.fetchone()[0]}")
    cursor.execute(f"SELECT * FROM \"{t}\" LIMIT 1")
    row = cursor.fetchone()
    col_names = [d[0] for d in cursor.description]
    print(f"Cols: {col_names}")
    print(f"Sample row: {row}")
conn.close()


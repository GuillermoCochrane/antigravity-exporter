import sqlite3
import os

BASE_DIR = r"C:\Users\cochr\.gemini\antigravity"
SUMMARIES_DB = os.path.join(BASE_DIR, "conversation_summaries.db")
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"
PB_FILE = os.path.join(BASE_DIR, "conversations", f"{CONV_ID}.pb")

print(f"--- FTS para {CONV_ID} ---")
conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()
cursor.execute("SELECT chunk_index, chunk_first_step, chunk_last_step, length(user_body), length(agent_body) FROM conversations_fts WHERE conversation_id = ? ORDER BY chunk_index", (CONV_ID,))
chunks = cursor.fetchall()
print(f"Total chunks en FTS: {len(chunks)}")
for c in chunks:
    print(f"  Chunk {c[0]}: steps {c[1]}-{c[2]} | user_body len: {c[3]} | agent_body len: {c[4]}")

print(f"\n--- Inspeccionando cabecera de {PB_FILE} ---")
if os.path.exists(PB_FILE):
    size = os.path.getsize(PB_FILE)
    print(f"Tamaño archivo: {size} bytes ({size / (1024*1024):.2f} MB)")
    with open(PB_FILE, "rb") as f:
        head = f.read(256)
        print(f"Primeros 64 bytes (hex): {head[:64].hex()}")
        print(f"Primeros 64 bytes (repr): {head[:64]}")
conn.close()


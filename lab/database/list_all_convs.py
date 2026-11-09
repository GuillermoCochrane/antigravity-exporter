import sqlite3

SUMMARIES_DB = r"C:\Users\cochr\.gemini\antigravity\conversation_summaries.db"
conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()

cursor.execute("SELECT conversation_id, title, preview, last_modified_time, workspace_uris, step_count FROM conversation_summaries ORDER BY last_modified_time ASC")
rows = cursor.fetchall()
print(f"Total conversations: {len(rows)}\n")

for cid, title, preview, last_mod, ws, steps in rows:
    name = (title or preview or "").strip()
    print(f"ID: {cid} | Steps: {steps:<5} | Mod: {last_mod[:10]} | Name: {name[:35]:<35} | WS: {ws}")

conn.close()


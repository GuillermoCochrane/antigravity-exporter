import sqlite3

SUMMARIES_DB = r"C:\Users\cochr\.gemini\antigravity\conversation_summaries.db"
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"

conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()

cursor.execute("SELECT chunk_index, user_body, agent_body FROM conversations_fts WHERE conversation_id = ? AND chunk_index = 0", (CONV_ID,))
row = cursor.fetchone()
if row:
    print(f"user_body strip (len {len(row[1])}):")
    print(repr(row[1].strip()[:300]))
    print(f"agent_body strip (len {len(row[2])}):")
    print(repr(row[2].strip()[:300]))
conn.close()

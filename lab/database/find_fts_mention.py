import sqlite3
import os

SUMMARIES_DB = r"C:\Users\cochr\.gemini\antigravity\conversation_summaries.db"
conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()

cursor.execute("SELECT conversation_id, title, user_body, agent_body FROM conversations_fts WHERE agent_body LIKE '%Antigravity-Database-Manager%' LIMIT 1")
row = cursor.fetchone()
if row:
    print("Conversation ID:", row[0])
    print("Title:", row[1])
    print("User body snippet:", row[2][:300] if row[2] else "")
    print("Agent body snippet:", row[3][:300] if row[3] else "")
else:
    print("No se encontro")
conn.close()


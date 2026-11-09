import sqlite3

SUMMARIES_DB = r"C:\Users\cochr\.gemini\antigravity\conversation_summaries.db"
CONV_ID = "1cfae999-9108-4b5e-955e-667dd3eeee89"

conn = sqlite3.connect(SUMMARIES_DB)
cursor = conn.cursor()

cursor.execute("SELECT chunk_index, chunk_first_step, chunk_last_step, user_body, agent_body FROM conversations_fts WHERE conversation_id = ? ORDER BY chunk_index", (CONV_ID,))
chunks = cursor.fetchall()

print(f"Total chunks for {CONV_ID}: {len(chunks)}")
for c in chunks:
    idx, first_s, last_s, ubody, abody = c
    u_lines = [l for l in ubody.split("\n") if l.strip()]
    a_lines = [l for l in abody.split("\n") if l.strip()]
    print(f"\n--- Chunk {idx} (steps {first_s} to {last_s}) ---")
    print(f"User non-empty lines: {len(u_lines)} | total chars: {len(ubody)}")
    for line in u_lines[:5]:
        print("  U:", line[:80])
    print(f"Agent non-empty lines: {len(a_lines)} | total chars: {len(abody)}")
    for line in a_lines[:3]:
        print("  A:", line[:80])

conn.close()


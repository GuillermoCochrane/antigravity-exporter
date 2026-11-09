import sqlite3
import os

PB_PATH = r"C:\Users\cochr\.gemini\antigravity\conversations\1cfae999-9108-4b5e-955e-667dd3eeee89.pb"

with open(PB_PATH, "rb") as f:
    header = f.read(100)

print("Header hex:", header[:32].hex())
print("Header repr:", header[:32])

try:
    conn = sqlite3.connect(PB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("SQLite tables:", cursor.fetchall())
    conn.close()
except Exception as e:
    print("Not sqlite:", e)


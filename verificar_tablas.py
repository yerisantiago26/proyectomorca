import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'morca.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = [fila[0] for fila in cursor.fetchall()]
conn.close()

print("📋 Tablas encontradas en morca.db:")
for t in tablas:
    print(f" - {t}")

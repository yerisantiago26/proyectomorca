import sqlite3

conn = sqlite3.connect('db/morca.db')  # Asegúrate que la carpeta "db" y el archivo existan
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    estado TEXT DEFAULT 'activa',
    avance INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()
print("✅ Tabla 'obras' creada o verificada.")

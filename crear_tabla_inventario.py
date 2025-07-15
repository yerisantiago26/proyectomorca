import sqlite3

conn = sqlite3.connect('db/morca.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    cantidad INTEGER NOT NULL,
    categoria TEXT,
    foto TEXT,
    obra_id INTEGER,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
)
''')

conn.commit()
conn.close()
print("✅ Tabla 'inventario' creada o verificada.")

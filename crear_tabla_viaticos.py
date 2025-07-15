import sqlite3

conn = sqlite3.connect('db/morca.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS viaticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER NOT NULL,
    obra_id INTEGER,
    concepto TEXT,
    monto REAL NOT NULL,
    fecha TEXT NOT NULL,
    observacion TEXT,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
    FOREIGN KEY (obra_id) REFERENCES obras(id)
)
''')

conn.commit()
conn.close()
print("✅ Tabla 'viaticos' creada o verificada.")

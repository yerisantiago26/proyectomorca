import sqlite3

# Ajusta la ruta si tu morca.db está en otro subdirectorio (por ejemplo 'db/morca.db')
DB_PATH = 'morca.db'

usuarios = [
    ('admin',    'admin123',   'universal'),
    ('jefe1',    'jefe123',    'jefe_obra'),
    ('usuario1', 'usuario123', 'estandar'),
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Si la tabla usuarios no existe, créala
c.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    clave   TEXT NOT NULL,
    rol     TEXT NOT NULL
);
""")

# Inserta o ignora si ya existe
c.executemany(
    "INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?);",
    usuarios
)

conn.commit()
conn.close()

print("Usuarios de prueba insertados correctamente.")

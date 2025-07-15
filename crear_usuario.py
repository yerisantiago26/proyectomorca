import sqlite3

DB_PATH = 'db/morca.db'  # Ajusta si tu ruta es distinta

# Conexión a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        clave TEXT,
        rol TEXT
    )
''')

# Crear un usuario de prueba
usuario = 'admin'
clave = 'admin2025'
rol = 'admin'

try:
    cursor.execute("INSERT INTO usuarios (nombre, clave, rol) VALUES (?, ?, ?)", (usuario, clave, rol))
    conn.commit()
    print(f"✅ Usuario '{usuario}' creado correctamente.")
except sqlite3.IntegrityError:
    print(f"⚠️ El usuario '{usuario}' ya existe.")

conn.close()


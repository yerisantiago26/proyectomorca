import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Tabla de usuarios (para login y control por rol)
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    clave TEXT NOT NULL,
    rol TEXT NOT NULL
)
''')

# 2. Tabla de obras (para vincular empleados, horas, compras)
cursor.execute('''
CREATE TABLE IF NOT EXISTS obras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    estado TEXT DEFAULT 'activa',
    progreso INTEGER DEFAULT 0,
    fecha_inicio TEXT,
    fecha_cierre TEXT
)
''')

# 3. Tabla de empleados (perfil extendido)
cursor.execute('''
CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    area TEXT,
    pago_hora REAL,
    telefono TEXT,
    tipo_sangre TEXT,
    alergias TEXT,
    enfermedades TEXT,
    nota TEXT,
    foto TEXT,
    obra_id INTEGER,
    FOREIGN KEY (obra_id) REFERENCES obras(id)
)
''')

# 4. Tabla de registro de horas trabajadas
cursor.execute('''
CREATE TABLE IF NOT EXISTS horas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER,
    fecha TEXT,
    lugar TEXT,
    dia TEXT,
    horas REAL,
    foto_avance TEXT,
    descripcion_avance TEXT,
    obra_id INTEGER,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
    FOREIGN KEY (obra_id) REFERENCES obras(id)
)
''')

# 5. Tabla de compras (facturas + vinculación con obras y empleados)
cursor.execute('''
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER,
    obra_id INTEGER,
    descripcion TEXT,
    codigo TEXT,
    imagen TEXT,
    ubicacion TEXT,
    fecha TEXT,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id),
    FOREIGN KEY (obra_id) REFERENCES obras(id)
)
''')

# 6. Tabla de inventario (productos generales)
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT,
    cantidad INTEGER,
    unidad TEXT,
    ubicacion TEXT,
    fecha_ingreso TEXT
)
''')


conn.commit()
conn.close()
print("✅ Base de datos creada correctamente en:", DB_PATH)

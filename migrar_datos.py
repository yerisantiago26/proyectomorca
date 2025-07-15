import json
import sqlite3
import os
from config import DB_PATH

# Ruta a la carpeta donde están los JSON
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Conexión a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -------------------------
# FUNCIONES AUXILIARES
# -------------------------

def get_obra_id(nombre_obra):
    """Devuelve el ID de una obra. La crea si no existe."""
    cursor.execute("SELECT id FROM obras WHERE nombre = ?", (nombre_obra,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO obras (nombre) VALUES (?)", (nombre_obra,))
        conn.commit()
        return cursor.lastrowid

def get_empleado_id(nombre_empleado):
    """Devuelve el ID del empleado. Lo crea si no existe."""
    cursor.execute("SELECT id FROM empleados WHERE nombre = ?", (nombre_empleado,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        # Inserta con valores mínimos por ahora
        cursor.execute("""
            INSERT INTO empleados (nombre, area, pago_hora)
            VALUES (?, ?, ?)
        """, (nombre_empleado, "Por definir", 0))
        conn.commit()
        return cursor.lastrowid

# -------------------------
# MIGRAR EMPLEADOS
# -------------------------

empleados_path = os.path.join(DATA_DIR, 'empleados.json')
with open(empleados_path, 'r', encoding='utf-8') as f:
    empleados = json.load(f)

for e in empleados:
    cursor.execute("SELECT id FROM empleados WHERE nombre = ?", (e['nombre'],))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO empleados
            (nombre, area, pago_hora, telefono, tipo_sangre, alergias, enfermedades, nota, foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e['nombre'],
            e.get('area', ''),
            e.get('pago_hora', 0),
            e.get('telefono', ''),
            e.get('tipo_sangre', ''),
            e.get('alergias', ''),
            e.get('enfermedades', ''),
            e.get('nota', ''),
            e.get('foto', '')
        ))

conn.commit()
print("✅ Empleados migrados.")

# -------------------------
# MIGRAR OBRAS (obras.json)
# -------------------------

obras_path = os.path.join(DATA_DIR, 'obras.json')
with open(obras_path, 'r', encoding='utf-8') as f:
    obras = json.load(f)

for obra in obras:
    cursor.execute("SELECT id FROM obras WHERE nombre = ?", (obra['nombre'],))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO obras (nombre, estado, progreso, fecha_inicio, fecha_cierre)
            VALUES (?, ?, ?, ?, ?)
        """, (
            obra['nombre'],
            obra.get('estado', 'activa'),
            obra.get('progreso', 0),
            obra.get('fecha_inicio', ''),
            obra.get('fecha_cierre', '')
        ))

conn.commit()
print("✅ Obras migradas.")

# -------------------------
# MIGRAR HORAS TRABAJADAS
# -------------------------

horas_path = os.path.join(DATA_DIR, 'horas_trabajadas.json')
with open(horas_path, 'r', encoding='utf-8') as f:
    horas = json.load(f)

for h in horas:
    empleado_id = get_empleado_id(h['nombre'])
    obra_id = get_obra_id(h.get('lugar', 'Obra sin nombre'))

    cursor.execute("""
        INSERT INTO horas
        (empleado_id, fecha, lugar, dia, horas, foto_avance, descripcion_avance, obra_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        empleado_id,
        h['fecha'],
        h['lugar'],
        h['dia'],
        h['horas'],
        h.get('foto_avance', ''),
        h.get('descripcion', ''),
        obra_id
    ))

conn.commit()
print("✅ Horas trabajadas migradas.")

# -------------------------
# MIGRAR COMPRAS
# -------------------------

compras_path = os.path.join(DATA_DIR, 'compras.json')
with open(compras_path, 'r', encoding='utf-8') as f:
    compras = json.load(f)

for c in compras:
    empleado_id = get_empleado_id(c['empleado'])
    obra_id = get_obra_id(c['obra'])

    cursor.execute("""
        INSERT INTO compras
        (empleado_id, obra_id, descripcion, codigo, imagen, ubicacion, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        empleado_id,
        obra_id,
        c['descripcion'],
        c['codigo'],
        c['imagen'],
        c['ubicacion'],
        c['fecha']
    ))

conn.commit()
print("✅ Compras migradas.")

conn.close()
print("🎉 Migración finalizada con éxito.")

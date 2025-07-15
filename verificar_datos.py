import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ----------------------------------------
# Mostrar empleados
print("\n🧑‍🔧 EMPLEADOS:")
cursor.execute("SELECT id, nombre, area, pago_hora, telefono FROM empleados")
for row in cursor.fetchall():
    print(row)

# ----------------------------------------
# Mostrar obras
print("\n🏗️  OBRAS:")
cursor.execute("SELECT id, nombre, estado, progreso FROM obras")
for row in cursor.fetchall():
    print(row)

# ----------------------------------------
# Mostrar horas trabajadas
print("\n⏱️  HORAS TRABAJADAS:")
cursor.execute("""
SELECT h.id, e.nombre, h.fecha, h.horas, h.lugar
FROM horas h
JOIN empleados e ON h.empleado_id = e.id
""")
for row in cursor.fetchall():
    print(row)

# ----------------------------------------
# Mostrar compras
print("\n🧾 COMPRAS:")
cursor.execute("""
SELECT c.id, e.nombre, o.nombre, c.descripcion, c.codigo
FROM compras c
JOIN empleados e ON c.empleado_id = e.id
JOIN obras o ON c.obra_id = o.id
""")
for row in cursor.fetchall():
    print(row)

conn.close()

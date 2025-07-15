from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'morca_ultra_secreto'
app.config['UPLOAD_FOLDER_EMPLEADOS'] = 'static/uploads/fotos_empleados'
app.config['UPLOAD_FOLDER_FACTURAS'] = 'static/uploads/facturas'
app.config['UPLOAD_FOLDER_UBICACIONES'] = 'static/uploads/ubicaciones'
DB = 'db/morca.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            clave TEXT,
            rol TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE NOT NULL,
            area TEXT,
            sangre TEXT,
            nota TEXT,
            estado TEXT,
            foto TEXT,
            precio_hora REAL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            estado TEXT,
            nota TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            obra_id INTEGER,
            checklist TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS horas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER,
            obra_id INTEGER,
            area_id INTEGER,
            jefe_obra_id INTEGER,
            horas REAL,
            fecha TEXT,
            foto TEXT,
            observaciones TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quien TEXT,
            obra_id INTEGER,
            area_id INTEGER,
            descripcion TEXT,
            ticket TEXT,
            ubicacion TEXT,
            codigo TEXT,
            fecha TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensaje TEXT,
            para_usuario TEXT,
            fecha TEXT
        )''')
        # Usuarios demo
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES ('admin', 'admin123', 'universal')")
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES ('jefeobra', 'jefe123', 'jefe_obra')")
        c.execute("INSERT OR IGNORE INTO usuarios (usuario, clave, rol) VALUES ('estandar', 'user123', 'estandar')")
        conn.commit()


@app.route('/')
def inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('inicio.html')
@app.route('/')
def index():
    if 'usuario' in session:
        rol = session.get('rol')
        if rol == 'jefe_obra':
            return render_template('inicio_jefe_obra.html')
        else:
            return render_template('inicio.html')
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        clave = request.form['clave']
        conn = get_db()
        # Busca el usuario y la clave en la tabla
        fila = conn.execute(
            "SELECT usuario, rol FROM usuarios WHERE usuario = ? AND clave = ?",
            (user, clave)
        ).fetchone()
        conn.close()
        if fila:
            session['usuario'] = fila['usuario']
            session['rol']     = fila['rol']
            # Si quieres guardar empleado_id para jefe de obra:
            if fila['rol'] == 'jefe_obra':
                # suponiendo que emp.id = usuarios.id, o puedes enlazar otra tabla
                session['empleado_id'] = fila['usuario']  # ajusta según tu lógica
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ... Aquí irán los módulos: empleados, obras, horas, compras, resúmenes, configuración, notificaciones, etc.
from flask import send_from_directory

# --- EMPLEADOS (CRUD) ---

@app.route('/empleados')
def empleados():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    empleados = db.execute("SELECT * FROM empleados").fetchall()
    puede_ver_precio = session['rol'] in ['universal', 'estandar']
    return render_template('empleados.html', empleados=empleados, puede_ver_precio=puede_ver_precio)

@app.route('/empleados/registro', methods=['GET', 'POST'])
def registro_empleado():
    if 'usuario' not in session or session['rol'] not in ['universal', 'estandar']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        area = request.form['area']
        sangre = request.form['sangre']
        nota = request.form['nota']
        estado = request.form['estado']
        precio_hora = request.form['precio_hora'] if session['rol'] in ['universal', 'estandar'] else 0
        foto = request.files['foto']
        filename = ""
        if foto:
            filename = secure_filename(f"{nombre}_{foto.filename}")
            foto.save(os.path.join(app.config['UPLOAD_FOLDER_EMPLEADOS'], filename))
        db = get_db()
        db.execute("INSERT INTO empleados (nombre, area, sangre, nota, estado, foto, precio_hora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (nombre, area, sangre, nota, estado, filename, precio_hora))
        db.commit()
        flash('Empleado registrado correctamente')
        return redirect(url_for('empleados'))
    return render_template('registro_empleado.html')


# --- OBRAS Y ÁREAS ---

@app.route('/obras')
def obras():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    obras = db.execute("SELECT * FROM obras").fetchall()
    # Admin y estándar pueden ver todas, jefe solo las asignadas (aquí simula todas)
    puede_editar = session['rol'] in ['universal', 'estandar']
    return render_template('obras.html', obras=obras, puede_editar=puede_editar)

@app.route('/obras/registro', methods=['GET', 'POST'])
def registro_obra():
    if 'usuario' not in session or session['rol'] not in ['universal', 'estandar']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        estado = request.form['estado']
        nota = request.form['nota']
        db = get_db()
        db.execute("INSERT INTO obras (nombre, estado, nota) VALUES (?, ?, ?)",
                   (nombre, estado, nota))
        db.commit()
        flash('Obra registrada correctamente')
        return redirect(url_for('obras'))
    return render_template('registro_obra.html')


# --- ÁREAS DE OBRA ---

@app.route('/obras/<int:obra_id>/areas')
def areas_obra(obra_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    obra = db.execute("SELECT * FROM obras WHERE id=?", (obra_id,)).fetchone()
    areas = db.execute("SELECT * FROM areas WHERE obra_id=?", (obra_id,)).fetchall()
    puede_editar = session['rol'] in ['universal', 'estandar']
    return render_template('areas.html', obra=obra, areas=areas, puede_editar=puede_editar)

@app.route('/obras/<int:obra_id>/areas/registro', methods=['GET', 'POST'])
def registro_area(obra_id):
    if 'usuario' not in session or session['rol'] not in ['universal', 'estandar']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nombre = request.form['nombre']
        checklist = request.form['checklist']  # Guarda como texto (1 tarea por línea)
        db = get_db()
        db.execute("INSERT INTO areas (nombre, obra_id, checklist) VALUES (?, ?, ?)",
                   (nombre, obra_id, checklist))
        db.commit()
        flash('Área registrada correctamente')
        return redirect(url_for('areas_obra', obra_id=obra_id))
    return render_template('registro_area.html', obra_id=obra_id)





  # asegúrate de tener este import arriba en tu app.py



@app.route('/resumen_individual/<int:empleado_id>')
def resumen_individual(empleado_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    emp = db.execute("SELECT * FROM empleados WHERE id=?", (empleado_id,)).fetchone()
    # Solo muestra precio/hora si rol lo permite
    puede_ver_precio = session['rol'] in ['universal', 'estandar']
    # Horas trabajadas del empleado
    horas = db.execute("""
        SELECT h.*, o.nombre AS obra, a.nombre AS area
        FROM horas h
        LEFT JOIN obras o ON h.obra_id = o.id
        LEFT JOIN areas a ON h.area_id = a.id
        WHERE h.empleado_id=?
        ORDER BY h.fecha DESC
    """, (empleado_id,)).fetchall()
    total_horas = sum([h['horas'] for h in horas])
    total_salario = total_horas * emp['precio_hora'] if puede_ver_precio else None
    return render_template('resumen_indivdual.html')
@app.route('/resumen_obra/<int:obra_id>')
def resumen_obra(obra_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    obra = db.execute("SELECT * FROM obras WHERE id=?", (obra_id,)).fetchone()
    # Áreas asociadas
    areas = db.execute("SELECT * FROM areas WHERE obra_id=?", (obra_id,)).fetchall()
    # Empleados que trabajaron en esta obra
    empleados = db.execute("""
        SELECT DISTINCT e.* FROM empleados e
        INNER JOIN horas h ON h.empleado_id = e.id
        WHERE h.obra_id=?
    """, (obra_id,)).fetchall()
    # Horas y avance por checklist
    horas = db.execute("""
        SELECT h.*, e.nombre as empleado, a.nombre as area
        FROM horas h
        LEFT JOIN empleados e ON h.empleado_id = e.id
        LEFT JOIN areas a ON h.area_id = a.id
        WHERE h.obra_id=?
        ORDER BY h.fecha DESC
    """, (obra_id,)).fetchall()
    # Compras para esta obra
    compras = db.execute("SELECT * FROM compras WHERE obra_id=?", (obra_id,)).fetchall()
    # Avance % por checklist (experimental: muestra el # de checklist cumplidas / total)
    avance_total = 0
    checklist_hechos = 0
    checklist_total = 0
    for area in areas:
        checklist = (area['checklist'] or "").splitlines()
        checklist_total += len(checklist)
        # Aquí podrías marcar las tareas cumplidas desde la tabla de horas o registros de avance
    avance_porcentaje = int(100 * checklist_hechos / checklist_total) if checklist_total > 0 else 0
    puede_ver_precio = session['rol'] in ['universal', 'estandar']
    return render_template('resumen_obra.html', obra=obra, areas=areas, empleados=empleados, horas=horas, compras=compras, avance_porcentaje=avance_porcentaje, puede_ver_precio=puede_ver_precio)
@app.route('/panel_configuracion')
def panel_configuracion():
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    empleados = db.execute("SELECT * FROM empleados").fetchall()
    obras = db.execute("SELECT * FROM obras").fetchall()
    usuarios = db.execute("SELECT * FROM usuarios").fetchall()
    areas = db.execute("SELECT * FROM areas").fetchall()
    return render_template('panel_configuracion.html', empleados=empleados, obras=obras, usuarios=usuarios, areas=areas)
import json

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    # Horas trabajadas por semana (últimos 7 días)
    horas_por_dia = db.execute("""
        SELECT fecha, SUM(horas) as total
        FROM horas
        WHERE fecha >= date('now', '-6 days')
        GROUP BY fecha
        ORDER BY fecha
    """).fetchall()
    labels_dias = [row['fecha'] for row in horas_por_dia]
    data_dias = [row['total'] for row in horas_por_dia]

    # Ranking de empleados (por horas totales)
    ranking = db.execute("""
        SELECT e.nombre, SUM(h.horas) as total_horas
        FROM empleados e
        LEFT JOIN horas h ON h.empleado_id = e.id
        GROUP BY e.id
        ORDER BY total_horas DESC
        LIMIT 5
    """).fetchall()
    ranking_labels = [r['nombre'] for r in ranking]
    ranking_data = [r['total_horas'] or 0 for r in ranking]

    # Avance global de obras (simple, según estado)
    obras = db.execute("SELECT nombre, estado FROM obras").fetchall()
    obras_labels = [o['nombre'] for o in obras]
    obras_estados = [1 if o['estado']=='activa' else 0 for o in obras]

    # Empleados activos/inactivos
    total_activos = db.execute("SELECT COUNT(*) FROM empleados WHERE estado='activo'").fetchone()[0]
    total_inactivos = db.execute("SELECT COUNT(*) FROM empleados WHERE estado='inactivo'").fetchone()[0]

    # Solo muestra valores de precios a admin/estandar
    puede_ver_precio = session['rol'] in ['universal', 'estandar']

    return render_template('dashboard.html',
        labels_dias=json.dumps(labels_dias),
        data_dias=json.dumps(data_dias),
        ranking_labels=json.dumps(ranking_labels),
        ranking_data=json.dumps(ranking_data),
        obras_labels=json.dumps(obras_labels),
        obras_estados=json.dumps(obras_estados),
        total_activos=total_activos,
        total_inactivos=total_inactivos,
        puede_ver_precio=puede_ver_precio
    )
# --- Alta nuevo empleado ---
@app.route('/empleado/nuevo', methods=['GET', 'POST'])
def nuevo_empleado():
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        nombre = request.form['nombre']
        area = request.form['area']
        estado = request.form['estado']
        precio_hora = float(request.form['precio_hora'])
        db.execute("INSERT INTO empleados (nombre, area, estado, precio_hora) VALUES (?, ?, ?, ?)", 
                   (nombre, area, estado, precio_hora))
        db.commit()
        flash('Empleado agregado correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_empleado.html')

# --- Editar empleado ---
@app.route('/empleado/editar/<int:id>', methods=['GET', 'POST'])
def editar_empleado(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    emp = db.execute("SELECT * FROM empleados WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        nombre = request.form['nombre']
        area = request.form['area']
        estado = request.form['estado']
        precio_hora = float(request.form['precio_hora'])
        db.execute("UPDATE empleados SET nombre=?, area=?, estado=?, precio_hora=? WHERE id=?", 
                   (nombre, area, estado, precio_hora, id))
        db.commit()
        flash('Empleado editado correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_empleado.html', emp=emp)

# --- Baja (eliminar) empleado ---
@app.route('/empleado/eliminar/<int:id>')
def eliminar_empleado(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM empleados WHERE id=?", (id,))
    db.commit()
    flash('Empleado eliminado correctamente')
    return redirect(url_for('panel_configuracion'))
# --- Alta nueva obra ---
@app.route('/obra/nueva', methods=['GET', 'POST'])
def nueva_obra():
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        nombre = request.form['nombre']
        estado = request.form['estado']
        nota = request.form['nota']
        db.execute("INSERT INTO obras (nombre, estado, nota) VALUES (?, ?, ?)",
                   (nombre, estado, nota))
        db.commit()
        flash('Obra agregada correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_obra.html')

# --- Editar obra ---
@app.route('/obra/editar/<int:id>', methods=['GET', 'POST'])
def editar_obra(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    obra = db.execute("SELECT * FROM obras WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        nombre = request.form['nombre']
        estado = request.form['estado']
        nota = request.form['nota']
        db.execute("UPDATE obras SET nombre=?, estado=?, nota=? WHERE id=?",
                   (nombre, estado, nota, id))
        db.commit()
        flash('Obra editada correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_obra.html', obra=obra)

# --- Baja (eliminar) obra ---
@app.route('/obra/eliminar/<int:id>')
def eliminar_obra(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM obras WHERE id=?", (id,))
    db.commit()
    flash('Obra eliminada correctamente')
    return redirect(url_for('panel_configuracion'))
# --- Alta nueva área ---
@app.route('/area/nueva', methods=['GET', 'POST'])
def nueva_area():
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    obras = db.execute("SELECT id, nombre FROM obras").fetchall()
    if request.method == 'POST':
        nombre = request.form['nombre']
        obra_id = int(request.form['obra_id'])
        checklist = request.form['checklist']
        db.execute("INSERT INTO areas (nombre, obra_id, checklist) VALUES (?, ?, ?)",
                   (nombre, obra_id, checklist))
        db.commit()
        flash('Área de trabajo agregada correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_area.html', obras=obras)

# --- Editar área ---
@app.route('/area/editar/<int:id>', methods=['GET', 'POST'])
def editar_area(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    area = db.execute("SELECT * FROM areas WHERE id=?", (id,)).fetchone()
    obras = db.execute("SELECT id, nombre FROM obras").fetchall()
    if request.method == 'POST':
        nombre = request.form['nombre']
        obra_id = int(request.form['obra_id'])
        checklist = request.form['checklist']
        db.execute("UPDATE areas SET nombre=?, obra_id=?, checklist=? WHERE id=?",
                   (nombre, obra_id, checklist, id))
        db.commit()
        flash('Área editada correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_area.html', area=area, obras=obras)

# --- Baja (eliminar) área ---
@app.route('/area/eliminar/<int:id>')
def eliminar_area(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM areas WHERE id=?", (id,))
    db.commit()
    flash('Área eliminada correctamente')
    return redirect(url_for('panel_configuracion'))
# --- Alta nuevo usuario ---
@app.route('/usuario/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        rol = request.form['rol']
        db.execute("INSERT INTO usuarios (usuario, clave, rol) VALUES (?, ?, ?)",
                   (usuario, clave, rol))
        db.commit()
        flash('Usuario agregado correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_usuario.html')

# --- Editar usuario ---
@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        rol = request.form['rol']
        db.execute("UPDATE usuarios SET usuario=?, clave=?, rol=? WHERE id=?",
                   (usuario, clave, rol, id))
        db.commit()
        flash('Usuario editado correctamente')
        return redirect(url_for('panel_configuracion'))
    return render_template('form_usuario.html', user=user)

# --- Eliminar usuario ---
@app.route('/usuario/eliminar/<int:id>')
def eliminar_usuario(id):
    if 'usuario' not in session or session['rol'] != 'universal':
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id=?", (id,))
    db.commit()
    flash('Usuario eliminado correctamente')
    return redirect(url_for('panel_configuracion'))
from datetime import datetime

# --- Ver notificaciones (solo admin/universal) ---
@app.route('/notificaciones')
def notificaciones():
    if 'usuario' not in session or session['rol'] not in ['universal', 'admin']:
        return redirect(url_for('login'))
    db = get_db()
    notis = db.execute("SELECT * FROM notificaciones ORDER BY fecha DESC").fetchall()
    return render_template('notificaciones.html', notificaciones=notis)

# --- Enviar nueva notificación (todos los usuarios) ---
@app.route('/notificacion/nueva', methods=['GET', 'POST'])
def nueva_notificacion():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        usuario = session['usuario']
        rol = session['rol']
        obra = request.form.get('obra', '')
        area = request.form.get('area', '')
        mensaje = request.form['mensaje']
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        db.execute("INSERT INTO notificaciones (fecha, usuario, rol, obra, area, mensaje) VALUES (?, ?, ?, ?, ?, ?)",
                   (fecha, usuario, rol, obra, area, mensaje))
        db.commit()
        flash('Notificación enviada')
        return redirect(url_for('notificaciones'))
    # Opcional: puedes pasar aquí las obras y áreas para mostrar en un select
    return render_template('form_notificacion.html')
from datetime import datetime

@app.route('/registro_horas', methods=['GET', 'POST'])
def registro_horas():
    if 'usuario' not in session or session['rol'] != 'jefe_obra':
        return redirect(url_for('login'))
    db = get_db()
    empleados = db.execute("SELECT * FROM empleados WHERE estado='activo'").fetchall()
    obras = db.execute("SELECT * FROM obras WHERE estado='activo'").fetchall()
    areas = db.execute("SELECT * FROM areas").fetchall()
    hoy = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        empleado_id = request.form['empleado_id']
        obra_id = request.form['obra_id']
        area_id = request.form['area_id']
        fecha = request.form['fecha']
        horas = request.form['horas']
        observaciones = request.form.get('observaciones', '')
        foto = request.files['foto']
        # Guarda la foto con nombre seguro
        filename = secure_filename(f"{datetime.now().timestamp()}_{foto.filename}")
        carpeta_fotos = os.path.join(app.root_path, 'static', 'uploads', 'horas')
        os.makedirs(carpeta_fotos, exist_ok=True)
        foto.save(os.path.join(carpeta_fotos, filename))
        db.execute("""
            INSERT INTO horas_trabajadas 
            (fecha, empleado_id, obra_id, area_id, horas, foto, observaciones, jefe_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha, empleado_id, obra_id, area_id, horas, filename, observaciones, session['usuario']))
        db.commit()
        flash('Registro exitoso')
        return redirect(url_for('registro_horas'))
    return render_template('registro_horas.html', empleados=empleados, obras=obras, areas=areas, hoy=hoy)
@app.route('/resumen_horas')
def resumen_horas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    db = get_db()
    rol = session['rol']
    if rol == 'jefe_obra':
        # Solo muestra registros hechos por ese jefe
        horas = db.execute("""
            SELECT h.*, e.nombre as nombre_empleado, o.nombre as nombre_obra, a.nombre as nombre_area
            FROM horas_trabajadas h
            JOIN empleados e ON h.empleado_id = e.id
            JOIN obras o ON h.obra_id = o.id
            JOIN areas a ON h.area_id = a.id
            WHERE h.jefe_usuario = ?
            ORDER BY h.fecha DESC
        """, (session['usuario'],)).fetchall()
    else:
        # Universal/estandar ven todo
        horas = db.execute("""
            SELECT h.*, e.nombre as nombre_empleado, o.nombre as nombre_obra, a.nombre as nombre_area
            FROM horas_trabajadas h
            JOIN empleados e ON h.empleado_id = e.id
            JOIN obras o ON h.obra_id = o.id
            JOIN areas a ON h.area_id = a.id
            ORDER BY h.fecha DESC
        """).fetchall()
    return render_template('resumen_horas.html', horas=horas)
import random
import string

def generar_codigo_compra():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if 'usuario' not in session or session['rol'] != 'jefe_obra':
        return redirect(url_for('login'))
    db = get_db()
    obras = db.execute("SELECT * FROM obras WHERE estado='activo'").fetchall()
    if request.method == 'POST':
        quien = request.form['quien']
        obra_id = request.form['obra_id']
        descripcion = request.form.get('descripcion', '')
        ticket_foto = request.files['ticket_foto']
        ubicacion_foto = request.files['ubicacion_foto']
        fecha = datetime.now().strftime('%Y-%m-%d')
        # Guardar fotos
        ticket_filename = secure_filename(f"ticket_{datetime.now().timestamp()}_{ticket_foto.filename}")
        ubicacion_filename = secure_filename(f"ubicacion_{datetime.now().timestamp()}_{ubicacion_foto.filename}")
        carpeta_tickets = os.path.join(app.root_path, 'static', 'uploads', 'tickets')
        carpeta_ubicaciones = os.path.join(app.root_path, 'static', 'uploads', 'ubicaciones')
        os.makedirs(carpeta_tickets, exist_ok=True)
        os.makedirs(carpeta_ubicaciones, exist_ok=True)
        ticket_foto.save(os.path.join(carpeta_tickets, ticket_filename))
        ubicacion_foto.save(os.path.join(carpeta_ubicaciones, ubicacion_filename))
        # Código único
        codigo = generar_codigo_compra()
        db.execute("""
            INSERT INTO compras (fecha, quien, obra_id, ticket_foto, ubicacion_foto, descripcion, codigo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fecha, quien, obra_id, ticket_filename, ubicacion_filename, descripcion, codigo))
        db.commit()
        flash(f'Compra registrada con código {codigo}')
        return redirect(url_for('compras'))
    return render_template('compras.html', obras=obras)

if __name__ == '__main__':
    app.run(debug=True)


import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db', 'morca.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos_empleados')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SECRET_KEY = 'clave-secreta-muy-segura'

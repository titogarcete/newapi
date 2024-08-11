from flask import Flask, request, jsonify  # Importa Flask y otras utilidades para manejar solicitudes HTTP
import sqlite3  # Importa la biblioteca para trabajar con bases de datos SQLite
from datetime import datetime  # Importa datetime para manejar fechas y horas
from auths import autenticar_clave_api  # Importa el decorador de autenticación desde auths.py

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Función para obtener una conexión a la base de datos SQLite
def obtener_conexion_bd():
    # Conecta a la base de datos 'logs.db' y establece la fábrica de filas para acceder a los registros como diccionarios
    conn = sqlite3.connect('logs.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta para manejar las solicitudes GET y POST en /logs
@app.route('/logs', methods=['GET', 'POST'])
@autenticar_clave_api  # Aplica el decorador de autenticación a esta ruta
def manejar_logs():
    if request.method == 'GET':
        return obtener_logs()  # Maneja las solicitudes GET
    elif request.method == 'POST':
        return registrar_log()  # Maneja las solicitudes POST

# Función para manejar las solicitudes GET y devolver los logs almacenados
def obtener_logs():
    # Obtiene los parámetros de consulta de la URL
    fecha_inicio = request.args.get('fechaInicio')
    fecha_fin = request.args.get('fechaFin')
    nombre_servicio = request.args.get('nombreServicio')

    # Construye la consulta SQL y una lista de parámetros para los filtros
    consulta = 'SELECT * FROM logs WHERE 1=1'
    parametros = []

    if fecha_inicio:
        try:
            # Convierte la fecha de inicio a un formato adecuado para la consulta SQL
            fecha_inicio_parseada = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
            parametros.append(fecha_inicio_parseada)
            consulta += ' AND timestamp >= ?'
        except ValueError:
            return jsonify({"error": "Formato de fecha de inicio inválido. Use YYYY-MM-DD"}), 400

    if fecha_fin:
        try:
            # Convierte la fecha de fin a un formato adecuado para la consulta SQL
            fecha_fin_parseada = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
            parametros.append(fecha_fin_parseada)
            consulta += ' AND timestamp <= ?'
        except ValueError:
            return jsonify({"error": "Formato de fecha de fin inválido. Use YYYY-MM-DD"}), 400

    if nombre_servicio:
        # Añade el filtro por nombre de servicio si se proporciona
        parametros.append(nombre_servicio)
        consulta += ' AND nombre_servicio = ?'

    try:
        # Conecta a la base de datos y ejecuta la consulta
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        cursor.execute(consulta, parametros)
        logs = cursor.fetchall()

        # Retorna los logs en formato JSON
        return jsonify([dict(ix) for ix in logs]), 200
    except Exception as e:
        # Maneja cualquier error que ocurra durante la consulta
        print(e)
        return jsonify({"error": "Error consultando los logs"}), 500

# Función para manejar las solicitudes POST y almacenar un nuevo log
def registrar_log():
    # Obtiene el log en formato JSON del cuerpo de la solicitud
    log = request.get_json()
    if not log:
        return jsonify({"error": "Formato de log inválido"}), 400

    # Extrae los campos del log
    timestamp = log.get('timestamp')
    nombre_servicio = log.get('nombre_servicio')
    nivel_log = log.get('nivel_log')
    mensaje = log.get('mensaje')
    recibido_en = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if not all([timestamp, nombre_servicio, nivel_log, mensaje]):
        return jsonify({"error": "Faltan campos en el log"}), 400

    try:
        # Conecta a la base de datos y crea la tabla de logs si no existe
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                nombre_servicio TEXT NOT NULL,
                nivel_log TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                recibido_en TEXT NOT NULL
            )
        ''')
        # Inserta el nuevo log en la tabla
        cursor.execute('INSERT INTO logs (timestamp, nombre_servicio, nivel_log, mensaje, recibido_en) VALUES (?, ?, ?, ?, ?)',
                       (timestamp, nombre_servicio, nivel_log, mensaje, recibido_en))
        conn.commit()

        # Retorna una confirmación de éxito
        return jsonify({"mensaje": "Log recibido"}), 200
    except Exception

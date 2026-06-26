
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error as MySQLError

app = Flask(__name__)
# Habilitar CORS para todos los orígenes
CORS(app, origins="*")

# --- Configuración de la base de datos ---
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "contrasena"),
            database=os.getenv("DB_NAME", "directorio")
        )
        return connection
    except MySQLError as e:
        app.logger.error(f"Error conectando a MySQL: {e}")
        return None

# --- Helper para estructurar respuestas de error ---
def error_response(code, message, status_code):
    return jsonify({"code": code, "message": message}), status_code


# ==============================================================================
# ENDPOINTS DE MATERIAS
# ==============================================================================

@app.route('/api/v1/materias', methods=['GET'])
def get_materias():
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, clave, nombre, creditos FROM materias")
        materias = cursor.fetchall()
        return jsonify(materias), 200
    except MySQLError:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/materias', methods=['POST'])
def create_materia():
    data = request.get_json() or {}
    clave = data.get('clave')
    nombre = data.get('nombre')
    creditos = data.get('creditos')

    if not clave or not nombre:
        return error_response("VALIDATION_ERROR", "Datos de entrada inválidos", 400)

    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        query = "INSERT INTO materias (clave, nombre, creditos) VALUES (%s, %s, %s)"
        cursor.execute(query, (clave, nombre, creditos))
        conn.commit()
        
        nuevo_id = cursor.lastrowid
        return jsonify({
            "id": nuevo_id,
            "clave": clave,
            "nombre": nombre,
            "creditos": creditos
        }), 201
    except MySQLError as e:
        # Clave duplicada u otro error de integridad
        if e.errno == 1062:
            return error_response("VALIDATION_ERROR", f"La clave '{clave}' ya está registrada.", 400)
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/materias/<int:id>', methods=['GET'])
def get_materia_by_id(id):
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, clave, nombre, creditos FROM materias WHERE id = %s", (id,))
        materia = cursor.fetchone()
        
        if not materia:
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)
        
        return jsonify(materia), 200
    except MySQLError:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/materias/<int:id>', methods=['PUT'])
def update_materia(id):
    data = request.get_json() or {}
    clave = data.get('clave')
    nombre = data.get('nombre')
    creditos = data.get('creditos')

    if not clave or not nombre:
        return error_response("VALIDATION_ERROR", "Datos de entrada inválidos", 400)

    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        # Verificar existencia
        cursor.execute("SELECT id FROM materias WHERE id = %s", (id,))
        if not cursor.fetchone():
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)

        query = "UPDATE materias SET clave = %s, nombre = %s, creditos = %s WHERE id = %s"
        cursor.execute(query, (clave, nombre, creditos, id))
        conn.commit()

        return jsonify({
            "id": id,
            "clave": clave,
            "nombre": nombre,
            "creditos": creditos
        }), 200
    except MySQLError as e:
        if e.errno == 1062:
            return error_response("VALIDATION_ERROR", f"La clave '{clave}' ya está en uso.", 400)
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/materias/<int:id>', methods=['DELETE'])
def delete_materia(id):
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        # Verificar existencia
        cursor.execute("SELECT id FROM materias WHERE id = %s", (id,))
        if not cursor.fetchone():
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)

        cursor.execute("DELETE FROM materias WHERE id = %s", (id,))
        conn.commit()
        return '', 204
    except MySQLError as e:
        # Captura error si hay docentes asociados (Restricción de FK)
        if e.errno == 1451:
            return error_response("VALIDATION_ERROR", "No se puede eliminar la materia porque tiene docentes asignados.", 400)
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


# ==============================================================================
# ENDPOINTS DE DOCENTES
# ==============================================================================

@app.route('/api/v1/docentes', methods=['GET'])
def get_docentes():
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email, materia_id FROM docentes")
        docentes = cursor.fetchall()
        return jsonify(docentes), 200
    except MySQLError:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/docentes', methods=['POST'])
def create_docente():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    email = data.get('email')
    materia_id = data.get('materia_id')  # Puede ser None / Null

    if not nombre or not email:
        return error_response("VALIDATION_ERROR", "Datos de entrada inválidos", 400)

    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        query = "INSERT INTO docentes (nombre, email, materia_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, email, materia_id))
        conn.commit()

        nuevo_id = cursor.lastrowid
        return jsonify({
            "id": nuevo_id,
            "nombre": nombre,
            "email": email,
            "materia_id": materia_id
        }), 201
    except MySQLError as e:
        if e.errno == 1062:
            return error_response("VALIDATION_ERROR", f"El email '{email}' ya está registrado.", 400)
        if e.errno == 1452:
            return error_response("VALIDATION_ERROR", f"La materia con id {materia_id} no existe.", 400)
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/docentes/<int:id>', methods=['GET'])
def get_docente_by_id(id):
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email, materia_id FROM docentes WHERE id = %s", (id,))
        docente = cursor.fetchone()

        if not docente:
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)

        return jsonify(docente), 200
    except MySQLError:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/docentes/<int:id>', methods=['PUT'])
def update_docente(id):
    data = request.get_json() or {}
    nombre = data.get('nombre')
    email = data.get('email')
    materia_id = data.get('materia_id')

    if not nombre or not email:
        return error_response("VALIDATION_ERROR", "Datos de entrada inválidos", 400)

    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        # Verificar existencia
        cursor.execute("SELECT id FROM docentes WHERE id = %s", (id,))
        if not cursor.fetchone():
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)

        query = "UPDATE docentes SET nombre = %s, email = %s, materia_id = %s WHERE id = %s"
        cursor.execute(query, (nombre, email, materia_id, id))
        conn.commit()

        return jsonify({
            "id": id,
            "nombre": nombre,
            "email": email,
            "materia_id": materia_id
        }), 200
    except MySQLError as e:
        if e.errno == 1062:
            return error_response("VALIDATION_ERROR", f"El email '{email}' ya está en uso.", 400)
        if e.errno == 1452:
            return error_response("VALIDATION_ERROR", f"La materia con id {materia_id} no existe.", 400)
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


@app.route('/api/v1/docentes/<int:id>', methods=['DELETE'])
def delete_docente(id):
    conn = get_db_connection()
    if not conn:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)

    try:
        cursor = conn.cursor()
        # Verificar existencia
        cursor.execute("SELECT id FROM docentes WHERE id = %s", (id,))
        if not cursor.fetchone():
            return error_response("RESOURCE_NOT_FOUND", "El recurso solicitado no existe", 404)

        cursor.execute("DELETE FROM docentes WHERE id = %s", (id,))
        conn.commit()
        return '', 204
    except MySQLError:
        return error_response("INTERNAL_ERROR", "Error interno del servidor", 500)
    finally:
        conn.close()


if __name__ == '__main__':
    # El puerto 3000 según especifica el servidor base de OpenAPI
    app.run(host='0.0.0.0', port=3000, debug=True)

import base64
import jwt
import datetime
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config




app = Flask(__name__)
CORS(app)

#python api/app.py para correr la api pero lo haces en otra terminal ala del npm run dev


# Cargar la configuración de la base de datos
app.config.from_object(config['development'])  # Asegúrate de usar el entorno adecuado
conexion = MySQL(app)

# Ruta para verificar si el usuario y la contraseña existen en la base de datos
# Clave secreta para firmar el token
SECRET_KEY = 'hola'

@app.route('/api/usuarios/login', methods=['GET'])
def verificar_usuario():
    try:
        # Obtener los parámetros de la solicitud
        usuario = request.args.get('usrName')
        contraseña = request.args.get('password')
        
        if not usuario or not contraseña:
            return jsonify({'error': 'Faltan el nombre de usuario o la contraseña'}), 400
        
        # Conectar a la base de datos y consultar por el usuario y la contraseña
        cursor = conexion.connection.cursor()
        sql = '''SELECT idUsers, name, last_name, email, userName, type 
                 FROM users WHERE userName = %s AND password = %s'''
        cursor.execute(sql, (usuario, contraseña))
        datos = cursor.fetchone()  # Obtener un solo usuario que coincida
        
        cursor.close()

        if datos:
            # Si se encuentra el usuario, crear el token con el id del usuario
            usuario = {
                'id': datos[0],
                'nombre': datos[1],
                'apellido': datos[2],
                'email': datos[3],
                'usuario': datos[4],
                'tipo': datos[5]
            }

            # Crear un token con el ID del usuario, válido por 1 hora
            # Crear un token con el ID del usuario, válido por 1 hora
            token_data = {
                'id': usuario['id'],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }   

            token = jwt.encode(token_data, SECRET_KEY, algorithm='HS256')

            # Devolver el usuario junto con el token
            response = {
                'usuario': usuario,
                'token': token
            }

            return jsonify(response), 200  # Usuario encontrado y contraseña correcta

        else:
            # Si no se encuentra el usuario o la contraseña no es correcta
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 404

    except Exception as ex:
        print(f"Error al verificar el usuario: {ex}")
        return jsonify({'error': 'Error al verificar el usuario'}), 500
    
# Ruta para crear un nuevo usuario con un método POST
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    try:
        # Obtener datos del JSON en la solicitud
        data = request.get_json()
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        email = data.get('email')
        usuario = data.get('usuario')
        contraseña =data.get('contraseña'),
        tipo = data.get('tipo')
        
        # Verificar que todos los campos están presentes
        if not (nombre and apellido and email and usuario and contraseña and tipo):
            return jsonify({'error': 'Faltan datos del usuario'}), 400
        
        # Insertar datos en la base de datos
        cursor = conexion.connection.cursor()
        sql = '''INSERT INTO users (name, last_name, email, userName, password, type)
                 VALUES (%s, %s, %s, %s, %s, %s)'''
        cursor.execute(sql, (nombre, apellido, email, usuario, contraseña, tipo))
        conexion.connection.commit()  # Confirmar los cambios
        cursor.close()
        
        return jsonify({'mensaje': 'Usuario creado exitosamente'}), 201
    except Exception as ex:
        print(f"Error al crear el usuario: {ex}")
        return jsonify({'error': 'No se puede crear el usuario'}), 500
    
@app.route('/api/especialistas', methods=['GET'])
def obtener_especialistas():
    try:
        cursor = conexion.connection.cursor()
        sql = 'SELECT iddoctors, name, specialty, contact, email, description, image FROM doctors'
        cursor.execute(sql)
        datos = cursor.fetchall()  # Obtener todos los especialistas
        
        especialistas = []
        for fila in datos:
            # Convertir la imagen BLOB a una cadena base64
            image_data = fila[6]
            if image_data:
                imagen_base64 = base64.b64encode(image_data).decode('utf-8')
                imagen_url = f"data:image/jpeg;base64,{imagen_base64}"
            else:
                imagen_url = "../../../public/logo.png"  # Imagen por defecto si no existe

            especialista = {
                'id': fila[0],
                'nombre': fila[1],
                'especialidad': fila[2],
                'contacto': fila[3],
                'email': fila[4],
                'descripcion': fila[5],
                'imagen': imagen_url
            }
            especialistas.append(especialista)
        
        cursor.close()  # Cierra el cursor después de usarlo
        return jsonify(especialistas), 200  # Devuelve todos los especialistas como una lista
    except Exception as ex:
        print(f"Error al obtener los especialistas: {ex}")
        return jsonify({'error': 'No se puede obtener los especialistas'}), 500
    
@app.route('/api/especialistas/<int:id>', methods=['GET'])
def obtener_especialista(id):
    try:
        cursor = conexion.connection.cursor()
        sql = 'SELECT iddoctors, name, specialty, contact, email, description, image FROM doctors WHERE iddoctors = %s'
        cursor.execute(sql, (id,))
        datos = cursor.fetchone()  # Obtener el especialista específico

        if datos:
            # Convertir la imagen BLOB a base64
            image_data = datos[6]
            imagen_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}" if image_data else "../../../public/logo.png"

            especialista = {
                'id': datos[0],
                'nombre': datos[1],
                'especialidad': datos[2],
                'contacto': datos[3],
                'email': datos[4],
                'descripcion': datos[5],
                'imagen': imagen_url
            }
            return jsonify(especialista), 200
        else:
            return jsonify({'error': 'Especialista no encontrado'}), 404
    except Exception as ex:
        print(f"Error al obtener el especialista: {ex}")
        return jsonify({'error': 'No se puede obtener el especialista'}), 500
    
# Nueva ruta para obtener las ubicaciones de un doctor específico
from flask import request

@app.route('/api/doctores/<int:id_doctor>/ubicaciones', methods=['GET', 'POST'])
def manejar_ubicaciones_doctor(id_doctor):
    if request.method == 'GET':
        try:
            cursor = conexion.connection.cursor()
            sql = '''SELECT idlocations, street, number, link, schedules 
                     FROM locations 
                     WHERE id_doctor = %s'''
            cursor.execute(sql, (id_doctor,))
            datos = cursor.fetchall()
            
            ubicaciones = []
            for fila in datos:
                ubicacion = {
                    'id': fila[0],
                    'calle': fila[1],
                    'numero': fila[2],
                    'enlace': fila[3],
                    'horarios': fila[4]
                }
                ubicaciones.append(ubicacion)
            
            cursor.close()
            return jsonify(ubicaciones), 200
        except Exception as ex:
            print(f"Error al obtener las ubicaciones: {ex}")
            return jsonify({'error': 'No se pueden obtener las ubicaciones'}), 500

    elif request.method == 'POST':
        try:
            # Obtener los datos del cuerpo de la solicitud
            datos = request.json
            calle = datos.get('calle')
            numero = datos.get('numero')
            enlace = datos.get('enlace')
            horarios = datos.get('horarios')

            # Validar que los datos requeridos estén presentes
            if not all([calle, numero, enlace, horarios]):
                return jsonify({'error': 'Faltan datos requeridos'}), 400

            # Insertar la nueva ubicación en la base de datos
            cursor = conexion.connection.cursor()
            sql = '''INSERT INTO locations (street, number, link, schedules, id_doctor)
                     VALUES (%s, %s, %s, %s, %s)'''
            cursor.execute(sql, (calle, numero, enlace, horarios, id_doctor))
            conexion.connection.commit()
            cursor.close()

            return jsonify({'message': 'Ubicación agregada correctamente'}), 201
        except Exception as ex:
            print(f"Error al agregar la ubicación: {ex}")
            return jsonify({'error': 'No se pudo agregar la ubicación'}), 500

    
@app.route('/api/ubicaciones', methods=['GET'])
def obtener_ubicaciones():
    try:
        cursor = conexion.connection.cursor()
        # Modificar la consulta para incluir el id_doctor
        sql = '''
            SELECT l.idlocations, l.street, l.number, l.link, l.schedules, l.id_doctor
            FROM locations l
        '''
        cursor.execute(sql)
        datos = cursor.fetchall()  # Obtener todas las ubicaciones
        
        ubicaciones = []
        for fila in datos:
            ubicacion = {
                'id': fila[0],
                'calle': fila[1],
                'numero': fila[2],
                'enlace': fila[3],
                'horarios': fila[4],
                'id_doctor': fila[5]  # Añadir id_doctor
            }
            ubicaciones.append(ubicacion)
        
        cursor.close()  # Cierra el cursor después de usarlo
        return jsonify(ubicaciones), 200  # Devuelve todas las ubicaciones como una lista
    except Exception as ex:
        print(f"Error al obtener las ubicaciones: {ex}")
        return jsonify({'error': 'No se pueden obtener las ubicaciones'}), 500


    
@app.route('/api/ubicaciones/<int:idlocation>', methods=['GET'])
def obtener_ubicacion(idlocation):
    try:
        # Crear un cursor para ejecutar la consulta SQL
        cursor = conexion.connection.cursor()
        
        # Modificar la consulta para incluir el id_doctor
        sql = '''
            SELECT l.idlocations, l.street, l.number, l.link, l.schedules, l.id_doctor
            FROM locations l
            WHERE l.idlocations = %s
        '''
        cursor.execute(sql, (idlocation,))
        datos = cursor.fetchone()  # Obtener la ubicación específica
        
        # Verificar si se encontró la ubicación
        if datos:
            # Crear un diccionario con los datos de la ubicación
            ubicacion = {
                'id': datos[0],
                'calle': datos[1],
                'numero': datos[2],
                'enlace': datos[3],
                'horarios': datos[4],
                'id_doctor': datos[5]  # Añadir id_doctor
            }
            cursor.close()
            return jsonify(ubicacion), 200  # Devolver la ubicación en formato JSON
        else:
            # Si no se encuentra la ubicación
            cursor.close()
            return jsonify({'error': 'Ubicación no encontrada'}), 404

    except Exception as ex:
        print(f"Error al obtener la ubicación: {ex}")
        return jsonify({'error': 'No se puede obtener la ubicación'}), 500


@app.route('/api/citas', methods=['GET', 'POST'])
def citas():
    if request.method == 'POST':
        try:
            # Obtener los datos de la cita desde la solicitud JSON
            data = request.get_json()
            patient = data.get('id_usr')
            doctor_id = data.get('doctor_id')
            location_id = data.get('location_id')
            appointment_date = data.get('appointment_date')  # Formato esperado: "YYYY-MM-DD"
            appointment_time = data.get('appointment_time')  # Formato esperado: "HH:MM"
            notes = data.get('notes')  # Opcional

            # Verificar que todos los campos necesarios están presentes
            if not (patient and doctor_id and location_id and appointment_date and appointment_time):
                return jsonify({'error': 'Faltan datos para crear la cita'}), 400

            # Crear la fecha completa de la cita
            appointment_datetime = f"{appointment_date} {appointment_time}:00"

            # Verificar si ya existe una cita en la misma hora, ignorando los minutos
            cursor = conexion.connection.cursor()
            sql_check = '''SELECT * FROM appointments 
                           WHERE id_doctor = %s 
                           AND id_ubication = %s 
                           AND DATE(appointment) = %s 
                           AND HOUR(appointment) = HOUR(%s)'''
            cursor.execute(sql_check, (doctor_id, location_id, appointment_date, appointment_datetime))
            existing_appointment = cursor.fetchone()

            if existing_appointment:
                # Cerrar cursor y devolver error si ya existe una cita en la misma hora
                cursor.close()
                return jsonify({'error': 'Ya existe una cita en este consultorio a la misma hora'}), 400

            # Insertar la nueva cita en la base de datos
            sql = '''INSERT INTO appointments (id_doctor, id_ubication, id_user, appointment, status, notes)
                     VALUES (%s, %s, %s, %s, 'pendiente', %s)'''
            cursor.execute(sql, (doctor_id, location_id, patient, appointment_datetime, notes))
            conexion.connection.commit()  # Confirmar los cambios en la base de datos
            cursor.close()

            return jsonify({'mensaje': 'Cita creada exitosamente'}), 201  # Cita creada correctamente
        except Exception as ex:
            print(f"Error al crear la cita: {ex}")
            return jsonify({'error': 'No se puede crear la cita'}), 500

    elif request.method == 'GET':
        try:
            # Obtener todas las citas de la base de datos
            cursor = conexion.connection.cursor()
            sql = '''SELECT a.idappointments, a.appointment, a.status, a.notes, a.name,
                            d.name as doctor_name, d.specialty,
                            l.street, l.number 
                     FROM appointments a
                     JOIN doctors d ON a.id_doctor = d.iddoctors
                     JOIN locations l ON a.id_ubication = l.idlocations'''
            cursor.execute(sql)
            citas = cursor.fetchall()  # Obtener todas las citas
            
            # Formatear los resultados en una lista de diccionarios
            citas_list = []
            for cita in citas:
                citas_list.append({
                    'id': cita[0],
                    'appointment': cita[1],
                    'status': cita[2],
                    'notes': cita[3],
                    'patient': cita[4],
                    'doctor_name': cita[5],
                    'specialty': cita[6],
                    'location': f"{cita[7]} {cita[8]}",
                })
            cursor.close()

            return jsonify(citas_list), 200  # Enviar la lista de citas como respuesta
        except Exception as ex:
            print(f"Error al obtener las citas: {ex}")
            return jsonify({'error': 'No se pueden obtener las citas'}), 500

@app.route('/api/citas/disponibles/<string:appointment_date>/<int:doctor_id>/<int:location_id>', methods=['GET'])
def obtener_horas_disponibles(appointment_date, doctor_id, location_id):
    try:
        # Validar que la fecha esté en el formato correcto
        datetime.strptime(appointment_date, '%Y-%m-%d')  # Verifica el formato YYYY-MM-DD

        cursor = conexion.connection.cursor()

        # Obtener solo las horas ocupadas con estado 'pendiente'
        sql = '''SELECT HOUR(appointment) as appointment_hour 
                 FROM appointments 
                 WHERE id_doctor = %s 
                 AND id_ubication = %s 
                 AND DATE(appointment) = %s 
                 AND status = 'pendiente' '''
        cursor.execute(sql, (doctor_id, location_id, appointment_date))
        ocupadas = [str(row[0]).zfill(2) + ":00" for row in cursor.fetchall()]
        cursor.close()

        # Crear un rango de horas entre 8:00 y 18:00
        horas_disponibles = []
        for h in range(8, 18):  # Esto va a incluir las 18:00
            hora_str = f"{str(h).zfill(2)}:00"
            # Verifica si la hora ya está ocupada
            if hora_str not in ocupadas:
                horas_disponibles.append(hora_str)

        return jsonify(horas_disponibles), 200
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use el formato YYYY-MM-DD'}), 400
    except Exception as ex:
        print(f"Error al obtener horas disponibles: {ex}")
        return jsonify({'error': 'Error al obtener las horas disponibles'}), 500


@app.route('/api/citas/<int:doctor_id>', methods=['GET'])
def get_citas_doctor(doctor_id):
    try:
        # Obtener todas las citas del doctor con el ID especificado
        cursor = conexion.connection.cursor()
        sql = '''SELECT a.idappointments, a.appointment, a.status, a.notes, 
                        u.name AS patient_name, u.last_name AS patient_last_name, u.email AS patient_email,
                        d.name AS doctor_name, d.specialty,
                        l.street, l.number 
                 FROM appointments a
                 JOIN doctors d ON a.id_doctor = d.iddoctors
                 JOIN locations l ON a.id_ubication = l.idlocations
                 JOIN users u ON a.id_user = u.idusers  -- Relación con la tabla de usuarios
                 WHERE a.id_doctor = %s'''
        cursor.execute(sql, (doctor_id,))
        citas = cursor.fetchall()  # Obtener todas las citas del doctor

        # Formatear los resultados en una lista de diccionarios
        citas_list = []
        for cita in citas:
            citas_list.append({
                'id': cita[0],
                'appointment': cita[1],
                'status': cita[2],
                'notes': cita[3],
                'patient': f"{cita[4]} {cita[5]}",  # Nombre completo del paciente
                'patient_email': cita[6],
                'doctor_name': cita[7],
                'specialty': cita[8],
                'location': f"{cita[9]} {cita[10]}"
            })
        cursor.close()

        return jsonify(citas_list), 200  # Enviar la lista de citas como respuesta
    except Exception as ex:
        print(f"Error al obtener las citas del doctor {doctor_id}: {ex}")
        return jsonify({'error': 'No se pueden obtener las citas del doctor especificado'}), 500



@app.route('/api/citas/usuario/<int:id_usuario>', methods=['GET', 'DELETE'])
def obtener_citas_usuario(id_usuario):
    try:
        # Si el método es GET, se obtienen las citas del usuario
        if request.method == 'GET':
            cursor = conexion.connection.cursor()
            sql = '''SELECT a.idappointments, a.appointment, a.status, a.notes, u.name AS patient_name, 
                            d.name AS doctor_name, d.specialty, l.street, l.number
                     FROM appointments a
                     JOIN doctors d ON a.id_doctor = d.iddoctors
                     JOIN locations l ON a.id_ubication = l.idlocations
                     JOIN users u ON a.id_user = u.idusers
                     WHERE a.id_user = %s'''  # Filtra por el id del usuario
            cursor.execute(sql, (id_usuario,))
            citas = cursor.fetchall()  # Obtener todas las citas del usuario

            # Formatear los resultados en una lista de diccionarios
            citas_list = []
            for cita in citas:
                citas_list.append({
                    'id': cita[0],
                    'appointment': cita[1],
                    'status': cita[2],
                    'notes': cita[3],
                    'patient_name': cita[4],
                    'doctor_name': cita[5],
                    'specialty': cita[6],
                    'location': f"{cita[7]} {cita[8]}",
                })
            cursor.close()
            return jsonify(citas_list), 200  # Enviar la lista de citas como respuesta

        # Si el método es DELETE, eliminamos una cita específica
        elif request.method == 'DELETE':
            cita_id = request.args.get('cita_id')  # Obtén el id de la cita desde los parámetros de la solicitud
            if not cita_id:
                return jsonify({'error': 'ID de cita no proporcionado'}), 400

            cursor = conexion.connection.cursor()
            sql = '''DELETE FROM appointments WHERE idappointments = %s AND id_user = %s'''
            cursor.execute(sql, (cita_id, id_usuario))  # Eliminar la cita para ese usuario específico
            conexion.connection.commit()  # Confirmar la eliminación en la base de datos
            cursor.close()

            return jsonify({'message': 'Cita eliminada con éxito'}), 200

    except Exception as ex:
        print(f"Error al manejar las citas del usuario {id_usuario}: {ex}")
        return jsonify({'error': 'No se puede procesar la solicitud'}), 500



@app.route('/api/usuarios/<int:id>', methods=['GET', 'PUT'])
def gestionar_usuario(id):
    if request.method == 'GET':
        try:
            # Crear un cursor para ejecutar la consulta SQL
            cursor = conexion.connection.cursor()

            # Modificar la consulta para obtener los datos del usuario por ID
            sql = '''SELECT idUsers, name, last_name, email, userName, password
                     FROM users WHERE idUsers = %s'''
            cursor.execute(sql, (id,))
            datos = cursor.fetchone()  # Obtener un solo usuario que coincida con el ID

            # Verificar si el usuario existe
            if datos:
                usuario = {
                    'id': datos[0],
                    'nombre': datos[1],
                    'apellido': datos[2],
                    'correo': datos[3],
                    'usuario': datos[4],
                    'contrasena': datos[5]
                }
                cursor.close()
                return jsonify(usuario), 200  # Devolver los datos del usuario
            else:
                cursor.close()
                return jsonify({'error': 'Usuario no encontrado'}), 404  # Si no existe el usuario
        except Exception as ex:
            print(f"Error al obtener el usuario: {ex}")
            return jsonify({'error': 'No se puede obtener el usuario'}), 500

    elif request.method == 'PUT':
        try:
            # Obtener los datos enviados en la solicitud PUT (suponiendo que es un JSON)
            datos_actualizados = request.get_json()

            # Validar que los datos requeridos estén presentes
            if not datos_actualizados.get('nombre') or not datos_actualizados.get('apellido') or not datos_actualizados.get('correo') or not datos_actualizados.get('usuario') or not datos_actualizados.get('contrasena'):
                return jsonify({'error': 'Faltan datos necesarios para actualizar el usuario'}), 400

            # Crear un cursor para ejecutar la consulta SQL
            cursor = conexion.connection.cursor()

            # Modificar la consulta para actualizar los datos del usuario
            sql = '''UPDATE users
                     SET name = %s, last_name = %s, email = %s, userName = %s, password = %s
                     WHERE idUsers = %s'''
            cursor.execute(sql, (datos_actualizados['nombre'], datos_actualizados['apellido'], datos_actualizados['correo'], datos_actualizados['usuario'], datos_actualizados['contrasena'], id))
            
            # Confirmar la actualización
            conexion.connection.commit()

            # Verificar si se actualizó algún registro
            if cursor.rowcount > 0:
                cursor.close()
                return jsonify({'message': 'Usuario actualizado con éxito'}), 200
            else:
                cursor.close()
                return jsonify({'error': 'Usuario no encontrado'}), 404  # Si no existe el usuario para actualizar
        except Exception as ex:
            print(f"Error al actualizar el usuario: {ex}")
            return jsonify({'error': 'No se puede actualizar el usuario'}), 500


@app.route('/api/doctores/<int:id_doctor>/ubicaciones/<int:id_ubicacion>', methods=['DELETE'])
def eliminar_ubicacion(id_doctor, id_ubicacion):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM locations WHERE id_doctor = %s AND idlocations = %s"
        cursor.execute(sql, (id_doctor, id_ubicacion))
        conexion.connection.commit()
        cursor.close()
        return jsonify({'message': 'Ubicación eliminada correctamente'}), 200
    except Exception as ex:
        print(f"Error al eliminar la ubicación: {ex}")
        return jsonify({'error': 'No se puede eliminar la ubicación'}), 500






if __name__ == '__main__':
    app.run()

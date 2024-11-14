import base64
from flask import Flask, jsonify, request
from datetime import datetime
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
        sql = '''SELECT name, last_name, email, userName, type 
                 FROM users WHERE userName = %s AND password = %s'''
        cursor.execute(sql, (usuario, contraseña))
        datos = cursor.fetchone()  # Obtener un solo usuario que coincida
        
        cursor.close()

        if datos:
            # Si se encuentra el usuario, devolver los datos
            usuario = {
                'nombre': datos[0],
                'apellido': datos[1],
                'email': datos[2],
                'usuario': datos[3],
                'tipo': datos[4]
            }
            return jsonify(usuario), 200  # Usuario encontrado y contraseña correcta
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
@app.route('/api/doctores/<int:id_doctor>/ubicaciones', methods=['GET'])
def obtener_ubicaciones_doctor(id_doctor):
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
            user_id = data.get('user_id')
            doctor_id = data.get('doctor_id')
            location_id = data.get('location_id')
            appointment_date = data.get('appointment_date')  # Formato esperado: "YYYY-MM-DD"
            appointment_time = data.get('appointment_time')  # Formato esperado: "HH:MM"
            notes = data.get('notes')  # Opcional

            # Verificar que todos los campos necesarios están presentes
            if not (user_id and doctor_id and location_id and appointment_date and appointment_time):
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
            sql = '''INSERT INTO appointments (id_doctor, id_ubication, id_usr, appointment, status, notes)
                     VALUES (%s, %s, %s, %s, 'pendiente', %s)'''
            cursor.execute(sql, (doctor_id, location_id, user_id, appointment_datetime, notes))
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
            sql = '''SELECT a.idappointments, a.appointment, a.status, a.notes,
                            d.name as doctor_name, d.specialty,
                            l.street, l.number,
                            u.name as user_name, u.last_name
                     FROM appointments a
                     JOIN doctors d ON a.id_doctor = d.iddoctors
                     JOIN locations l ON a.id_ubication = l.idlocations
                     JOIN users u ON a.id_usr = u.idUsers'''
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
                    'doctor_name': cita[4],
                    'specialty': cita[5],
                    'location': f"{cita[6]} {cita[7]}",
                    'user_name': f"{cita[8]} {cita[9]}"
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
        for h in range(8, 19):  # Esto va a incluir las 18:00
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













if __name__ == '__main__':
    app.run()

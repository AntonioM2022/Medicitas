import base64
from flask import Flask, jsonify, request
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


if __name__ == '__main__':
    app.run()

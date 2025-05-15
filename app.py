#app.py
from flask import Flask, render_template, jsonify, request, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from models.usuario import Usuario
from routes.administrador_routes import administrador_bp
from config import init_db, db
from routes import blueprints
from flask import session
from config import Config

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# Inicialización de la base de datos
init_db(app)

# Registro de rutas
for bp in blueprints:
    if bp.name == "usuario_bp":
        app.register_blueprint(bp, url_prefix='/perfil')
    elif bp.name == "equipo_bp":
        app.register_blueprint(bp, url_prefix='/equipos')
    elif bp.name == "partido_bp":
        app.register_blueprint(bp, url_prefix='/partido')
    elif bp.name == "categoria_edad":
        app.register_blueprint(bp, url_prefix='/categoria_edad')
    elif bp.name == "categoria_sexo":
        app.register_blueprint(bp, url_prefix='/categoria_sexo')
    elif bp.name == "jugadas":
        app.register_blueprint(bp, url_prefix='/jugadas')
    elif bp.name == "rol":
        app.register_blueprint(bp, url_prefix='/rol')
    elif bp.name == "posicion":
        app.register_blueprint(bp, url_prefix='/posicion')
    elif bp.name == "detalle_jugada":
        app.register_blueprint(bp, url_prefix='/detalle_jugada')
    elif bp.name == "torneo":
        app.register_blueprint(bp, url_prefix='/torneo')
    elif bp.name == "equipo_rival":
        app.register_blueprint(bp, url_prefix='/equipo_rival')
    elif bp.name == "jugadores_rivales":
        app.register_blueprint(bp, url_prefix='/jugadores_rivales')
    elif bp.name == "mensajes":
        app.register_blueprint(bp, url_prefix='/mensajes')
    elif bp.name == "partido":
        app.register_blueprint(bp, url_prefix='/partido')
    elif bp.name == "usuario_equipo":
        app.register_blueprint(bp, url_prefix='/usuario_equipo')
    elif bp.name == "videos":
        app.register_blueprint(bp, url_prefix='/videos')
    elif bp.name == "deteccion":
        app.register_blueprint(bp, url_prefix='/deteccion')
    elif bp.name == "modalidad":
        app.register_blueprint(bp, url_prefix='/modalidad')
        
app.register_blueprint(administrador_bp, url_prefix='/administrador')


# Rutas
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Correo y contraseña son requeridos'}), 400

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, password):
            return jsonify({
                'documento': usuario.documento
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"mensaje": "Sesión cerrada"})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    if not nombre or not email or not password:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400

    # Hashear la contraseña antes de almacenarla
    hashed_password = generate_password_hash(password)

    nuevo_usuario = Usuario(nombre=nombre, email=email, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201

@app.context_processor
def inject_documento():
    return {'documento': None}

@app.route('/')
def home():
    documento = session.get('documento')  # o de la base de datos, o fijo para pruebas
    return render_template('base.html', documento=documento)

# Manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
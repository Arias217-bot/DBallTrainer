# models/usuario.py
from config import db
from models.entidad_base import EntidadBase
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(EntidadBase):
    __tablename__ = 'usuario'

    documento = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True)
    experiencia = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    id_tipo_usuario = db.Column(db.Integer)
    peso = db.Column(db.Numeric(5, 2))
    altura = db.Column(db.Numeric(5, 2))

    def set_password(self, password):
        """Hashea la contraseña antes de guardarla."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return check_password_hash(self.password, password)

    def from_dict(self, data):
        """Asigna valores desde un diccionario, asegurando que la contraseña se hashee."""
        for key, value in data.items():
            if key == "password":  # Si es la contraseña, la hasheamos antes de asignarla
                self.set_password(value)
            else:
                setattr(self, key, value)


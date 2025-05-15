# models/usuario_equipo.py
from config import db
from models.entidad_base import EntidadBase

class Usuario_Equipo(EntidadBase):
    __tablename__ = 'usuario_equipo'

    id_usuario_equipo = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Definir la clave primaria correcta
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipo.id_equipo'), nullable=False)
    documento = db.Column(db.String(20), db.ForeignKey('usuario.documento'), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    id_posicion = db.Column(db.Integer, db.ForeignKey('posicion.id_posicion'), nullable=False)
    numero = db.Column(db.Integer)

    equipo = db.relationship('Equipo', backref=db.backref('usuarios_equipo', cascade='all, delete-orphan'))
    usuario = db.relationship('Usuario', backref=db.backref('equipos', cascade='all, delete-orphan'))
    rol = db.relationship('Rol', backref='rol_asignado')
    posicion = db.relationship('Posicion', backref='usuarios_posiciones')
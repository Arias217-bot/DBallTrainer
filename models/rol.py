# models/rol.py
from config import db
from models.entidad_base import EntidadBase

class Rol(EntidadBase):
    __tablename__ = 'rol'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)

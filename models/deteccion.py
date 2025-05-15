# models/deteccion.py
from config import db
from models.entidad_base import EntidadBase

class Deteccion(EntidadBase):
    __tablename__ = 'deteccion'

    id_deteccion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

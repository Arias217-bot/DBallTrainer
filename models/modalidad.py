# models/modalidad.py
from config import db
from models.entidad_base import EntidadBase

class Modalidad(EntidadBase):
    __tablename__ = 'modalidad'

    id_modalidad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
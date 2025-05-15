from config import db
from models.entidad_base import EntidadBase

class Posicion(EntidadBase):
    __tablename__ = 'posicion'

    id_posicion = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
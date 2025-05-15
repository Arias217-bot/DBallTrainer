# models/equipo.py
from config import db
from models.entidad_base import EntidadBase # Para heredar de EntidadBase

class Equipo(EntidadBase):
    __tablename__ = 'equipo'

    id_equipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_categoria_edad = db.Column(db.Integer, nullable=False)
    id_categoria_sexo = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)

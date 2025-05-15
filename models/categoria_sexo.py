from config import db
from models.entidad_base import EntidadBase

class CategoriaSexo(EntidadBase):
    __tablename__ = 'categoria_sexo'

    id_categoria_sexo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
# models/entidad_base.py
from config import db

class EntidadBase(db.Model):
    __abstract__ = True  # Indica que esta clase no se crea como tabla

    def to_dict(self):
        """Convierte los atributos del modelo en un diccionario."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def from_dict(self, data):
        """Asigna valores a los atributos del modelo desde un diccionario."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

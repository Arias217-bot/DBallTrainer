# models/jugadores_rivales.py
from config import db
from models.entidad_base import EntidadBase
from models.equipo_rival import EquipoRival

class JugadoresRivales(EntidadBase):
    __tablename__ = 'jugadores_rivales'

    documento = db.Column(db.String(20), primary_key=True)
    nombre_equipo_rival = db.Column(
        db.String(50),
        db.ForeignKey('equipo_rival.nombre_equipo_rival', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    eps = db.Column(db.String(100))

    equipo_rival = db.relationship('EquipoRival', backref=db.backref('jugadores', cascade='all, delete-orphan'))

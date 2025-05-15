# models/equipo_rival.py
from config import db
from models.entidad_base import EntidadBase

class EquipoRival(EntidadBase):
    __tablename__ = 'equipo_rival'

    nombre_equipo_rival = db.Column(db.String(50), primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)
    director = db.Column(db.String(50), nullable=False)
    asistente = db.Column(db.String(50), nullable=False)
    director_cedula = db.Column(db.String(20), nullable=False)
    asistente_cedula = db.Column(db.String(20), nullable=False)
    id_torneo = db.Column(db.Integer, db.ForeignKey('torneo.id_torneo'), nullable=True)

    torneo = db.relationship('Torneo', backref='equipos_rivales')

# models/partido.py
from config import db
from models.entidad_base import EntidadBase

class Partido(EntidadBase):
    __tablename__ = 'partido'

    nombre_partido = db.Column(db.String(50), primary_key=True)  # Clave primaria
    id_torneo = db.Column(
        db.Integer,
        db.ForeignKey('torneo.id_torneo', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    nombre_equipo_rival = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(100), nullable=True)
    marcador_local = db.Column(db.Integer, nullable=False)
    marcador_rival = db.Column(db.Integer, nullable=False)
    video_url = db.Column(db.String(255), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    torneo = db.relationship('Torneo', backref=db.backref('Partidos', cascade='all, delete-orphan'))
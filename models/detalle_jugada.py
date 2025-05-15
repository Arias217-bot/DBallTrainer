# models/detalle_jugada.py
from config import db
from models.entidad_base import EntidadBase
from models.jugadas import Jugadas

class DetalleJugada(EntidadBase):
    __tablename__ = 'detalle_jugada'

    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_jugada = db.Column(db.Integer, db.ForeignKey('jugadas.id_jugada', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    jugador = db.Column(db.Integer, nullable=False)
    zona = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.String(3))

    jugada = db.relationship('Jugadas', backref=db.backref('detalles', cascade='all, delete-orphan'))

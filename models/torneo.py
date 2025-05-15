# models/torneo.py
from config import db
from models.entidad_base import EntidadBase
from models.equipo import Equipo

class Torneo(EntidadBase):
    __tablename__ = 'torneo'

    id_torneo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_torneo = db.Column(db.String(50), nullable=False, unique=True)
    id_equipo = db.Column(
        db.Integer,
        db.ForeignKey('equipo.id_equipo', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    descripcion = db.Column(db.Text)

    equipo = db.relationship('Equipo', backref=db.backref('torneos', cascade='all, delete-orphan'))

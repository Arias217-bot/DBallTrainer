# models/mensajes.py
from config import db
from models.entidad_base import EntidadBase
from models.equipo import Equipo

class Mensajes(EntidadBase):
    __tablename__ = 'mensajes'

    id_mensaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(
        db.Integer,
        db.ForeignKey('equipo.id_equipo', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    contenido = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    autor = db.Column(db.String(100))

    equipo = db.relationship('Equipo', backref=db.backref('mensajes', cascade='all, delete-orphan'))

# models/jugadas.py
from config import db
from models.entidad_base import EntidadBase

class Jugadas(EntidadBase):
    __tablename__ = 'jugadas'

    id_jugada = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_partido = db.Column(
        db.Integer,
        db.ForeignKey('partido.nombre_partido', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
    secuencia_jugada = db.Column(db.Text)

    # tiempo_inicio y tiempo_fin como columnas de tipo Time, necesario para su uso desde la 12 a la 30
    _tiempo_inicio = db.Column("tiempo_inicio", db.Time)
    _tiempo_fin = db.Column("tiempo_fin", db.Time)
    datos_procesados = db.Column(db.JSON)

    partido = db.relationship('Partido', backref=db.backref('jugadas', cascade='all, delete-orphan'))

    @property
    def tiempo_inicio(self):
        return self._tiempo_inicio.isoformat() if self._tiempo_inicio else None

    @tiempo_inicio.setter
    def tiempo_inicio(self, value):
        self._tiempo_inicio = value

    @property
    def tiempo_fin(self):
        return self._tiempo_fin.isoformat() if self._tiempo_fin else None

    @tiempo_fin.setter
    def tiempo_fin(self, value):
        self._tiempo_fin = value

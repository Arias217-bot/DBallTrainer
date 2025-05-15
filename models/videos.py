# models/video.py
from config import db
from models.entidad_base import EntidadBase

class Videos(EntidadBase):
    __tablename__ = 'videos'

    id_video = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    url_procesado = db.Column(db.String(255))
    documento_usuario = db.Column(db.String(20), db.ForeignKey('usuario.documento'), nullable=False)
    resultados_analisis = db.Column(db.JSON)

    id_modalidad = db.Column(db.Integer, db.ForeignKey('modalidad.id_modalidad'), nullable=False)
    id_deteccion = db.Column(db.Integer, db.ForeignKey('deteccion.id_deteccion'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('videos', lazy=True))
    modalidad = db.relationship('Modalidad', backref=db.backref('videos', lazy=True))
    deteccion = db.relationship('Deteccion', backref=db.backref('videos', lazy=True))

    def to_dict(self):
        base = super().to_dict()
        base['modalidad'] = self.modalidad.to_dict() if self.modalidad else None
        base['deteccion'] = self.deteccion.to_dict() if self.deteccion else None
        base['resultados_analisis'] = self.resultados_analisis if self.resultados_analisis else None
        return base
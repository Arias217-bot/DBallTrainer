# routes/usuario_routes.py
from routes.entidad_routes import EntidadRoutes
from models.usuario import Usuario

from flask import render_template
from config import db

# Blueprints
usuario_routes = EntidadRoutes('usuario', Usuario)
usuario_bp = usuario_routes.bp  # El Blueprint que usaremos en `app.py`

@usuario_bp.route('/ver/<documento>')
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('profile.html', usuario=usuario, documento=documento)
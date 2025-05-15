# routes/usuario_equipo_routes.py
from routes.entidad_routes import EntidadRoutes
from models.usuario_equipo import Usuario_Equipo

from flask import render_template, request
from config import db

# Blueprints
usuario_equipo_routes = EntidadRoutes('usuario_equipo', Usuario_Equipo)
usuario_equipo_bp = usuario_equipo_routes.bp
usuario_equipo_bp.name = "usuario_equipo"

@usuario_equipo_bp.route('/ver', endpoint='usuario_equipo_page')
def usuario_equipo_page():
    # Obtener el parámetro de búsqueda opcional (por ejemplo, por documento del usuario)
    query = request.args.get('q', '')
    if query:
        usuarios_equipos = db.session.query(Usuario_Equipo).join(Usuario_Equipo.usuario).filter(
            Usuario_Equipo.documento.ilike(f"%{query}%")
        ).all()
    else:
        usuarios_equipos = db.session.query(Usuario_Equipo).all()

    return render_template('usuario_equipo.html', usuarios_equipos=usuarios_equipos, q=query)

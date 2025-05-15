# routes/rol_routes.py
from routes.entidad_routes import EntidadRoutes
from models.rol import Rol

from flask import render_template, request
from config import db

# Blueprints
rol_routes = EntidadRoutes('rol', Rol)
rol_bp = rol_routes.bp
rol_bp.name = "rol"  # El Blueprint que usaremos en `app.py`

@rol_bp.route('/ver', endpoint='rol_page')
def rol_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        roles = db.session.query(Rol).filter(
            Rol.nombre.ilike(f"%{query}%")
        ).all()
    else:
        roles = db.session.query(Rol).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('rol.html', roles=roles, q=query)
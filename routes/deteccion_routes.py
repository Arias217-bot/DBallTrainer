# routes/deteccion_routes.py
from routes.entidad_routes import EntidadRoutes
from models.deteccion import Deteccion

from flask import render_template, request
from config import db

# Blueprints
deteccion_routes = EntidadRoutes('deteccion', Deteccion)
deteccion_bp = deteccion_routes.bp
deteccion_bp.name = "deteccion"  # El Blueprint que usaremos en `app.py`

@deteccion_bp.route('/ver', endpoint='deteccion_page')
def deteccion_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        detecciones = db.session.query(Deteccion).filter(
            Deteccion.nombre.ilike(f"%{query}%")
        ).all()
    else:
        detecciones = db.session.query(Deteccion).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('deteccion.html', detecciones=detecciones, q=query)
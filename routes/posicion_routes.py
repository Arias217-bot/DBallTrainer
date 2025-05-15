# routes/posicion_routes.py
from routes.entidad_routes import EntidadRoutes
from models.posicion import Posicion

from flask import render_template, request
from config import db

# Blueprints
posicion_routes = EntidadRoutes('posicion', Posicion)
posicion_bp = posicion_routes.bp
posicion_bp.name = "posicion"  # El Blueprint que usaremos en `app.py`

@posicion_bp.route('/ver', endpoint='posicion_page')
def posicion_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        posiciones = db.session.query(Posicion).filter(
            Posicion.nombre.ilike(f"%{query}%")
        ).all()
    else:
        posiciones = db.session.query(Posicion).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('posicion.html', posiciones=posiciones, q=query)
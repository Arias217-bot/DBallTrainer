# routes/jugadores_rivales_routes.py
from routes.entidad_routes import EntidadRoutes
from models.jugadores_rivales import JugadoresRivales

from flask import render_template, request
from config import db

# Blueprints
jugadores_rivales_routes = EntidadRoutes('jugadores_rivales', JugadoresRivales)
jugadores_rivales_bp = jugadores_rivales_routes.bp
jugadores_rivales_bp.name = "jugadores_rivales"  # El Blueprint que usaremos en `app.py`

@jugadores_rivales_bp.route('/ver', endpoint='jugadores_rivales_page')
def jugadores_rivales_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        jugadores_rivales_lista = db.session.query(JugadoresRivales).filter(
            JugadoresRivales.documento.ilike(f"%{query}%")
        ).all()
    else:
        jugadores_rivales_lista = db.session.query(JugadoresRivales).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('jugadores_rivales.html', jugadores_rivales_lista=jugadores_rivales_lista, q=query)
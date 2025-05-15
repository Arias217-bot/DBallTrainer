# routes/jugada_routes.py
from routes.entidad_routes import EntidadRoutes
from models.jugadas import Jugadas

from flask import render_template, request
from config import db

# Blueprints
jugadas_routes = EntidadRoutes('jugadas', Jugadas)
jugadas_bp = jugadas_routes.bp
jugadas_bp.name = "jugadas"  # El Blueprint que usaremos en `app.py`

@jugadas_bp.route('/ver', endpoint='jugadas_page')
def jugadas_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        jugadas_lista = db.session.query(Jugadas).filter(
            Jugadas.nombre.ilike(f"%{query}%")
        ).all()
    else:
        jugadas_lista = db.session.query(Jugadas).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('jugadas.html', jugadas_lista=jugadas_lista, q=query)
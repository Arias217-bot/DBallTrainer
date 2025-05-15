# routes/mensajes_routes.py
from routes.entidad_routes import EntidadRoutes
from models.mensajes import Mensajes
from flask import render_template, request
from config import db

# Blueprints
mensajes_routes = EntidadRoutes('mensajes', Mensajes)
mensajes_bp = mensajes_routes.bp
mensajes_bp.name = "mensajes"  # El Blueprint que usaremos en `app.py`

@mensajes_bp.route('/ver', endpoint='mensajes_page')
def mensajes_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        mensajes_lista = db.session.query(Mensajes).filter(
            Mensajes.nombre.ilike(f"%{query}%")
        ).all()
    else:
        mensajes_lista = db.session.query(Mensajes).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('mensajes.html', mensajes_lista=mensajes_lista, q=query)
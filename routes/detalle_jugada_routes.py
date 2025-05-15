# routes/detalle_jugada_routes.py
from routes.entidad_routes import EntidadRoutes
from models.detalle_jugada import DetalleJugada

from flask import render_template, request
from config import db

# Blueprints
detalle_jugada_routes = EntidadRoutes('detalle_jugada', DetalleJugada)
detalle_jugada_bp = detalle_jugada_routes.bp
detalle_jugada_bp.name = "detalle_jugada"  # El Blueprint que usaremos en `app.py`

@detalle_jugada_bp.route('/ver', endpoint='detalle_jugada_page')
def detalle_jugada_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por jugador (busqueda insensible a mayúsculas)
        detalles_jugadas = db.session.query(DetalleJugada).filter(
            DetalleJugada.orden.ilike(f"%{query}%")
        ).all()
    else:
        detalles_jugadas = db.session.query(DetalleJugada).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('detalle_jugada.html', detalles_jugadas=detalles_jugadas, q=query)
# routes/modalidad_routes.py
from routes.entidad_routes import EntidadRoutes
from models.modalidad import Modalidad

from flask import render_template, request
from config import db

# Blueprints
modalidad_routes = EntidadRoutes('modalidad', Modalidad)
modalidad_bp = modalidad_routes.bp
modalidad_bp.name = "modalidad"  # El Blueprint que usaremos en `app.py`

@modalidad_bp.route('/ver', endpoint='modalidad_page')
def modalidad_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        modalidades = db.session.query(Modalidad).filter(
            Modalidad.nombre.ilike(f"%{query}%")
        ).all()
    else:
        modalidades = db.session.query(Modalidad).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('modalidad.html', modalidades=modalidades, q=query)
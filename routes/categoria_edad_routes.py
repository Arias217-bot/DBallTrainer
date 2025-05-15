# routes/categoria_edad_routes.py
from routes.entidad_routes import EntidadRoutes
from models.categoria_edad import CategoriaEdad

from flask import render_template, request
from config import db

# Blueprints
categoria_edad_routes = EntidadRoutes('categoria_edad', CategoriaEdad)
categoria_edad_bp = categoria_edad_routes.bp
categoria_edad_bp.name = "categoria_edad"  # El Blueprint que usaremos en `app.py`

@categoria_edad_bp.route('/ver', endpoint='categoria_edad_page')
def categoria_edad_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        categorias_edad = db.session.query(CategoriaEdad).filter(
            CategoriaEdad.nombre.ilike(f"%{query}%")
        ).all()
    else:
        categorias_edad = db.session.query(CategoriaEdad).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('categoria_edad.html', 
                           categorias_edad=categorias_edad, 
                           q=query)
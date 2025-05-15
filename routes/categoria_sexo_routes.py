# routes/categoria_sexo_routes.py
from routes.entidad_routes import EntidadRoutes
from models.categoria_sexo import CategoriaSexo

from flask import render_template, request
from config import db

# Blueprints
categoria_sexo_routes = EntidadRoutes('categoria_sexo', CategoriaSexo)
categoria_sexo_bp = categoria_sexo_routes.bp
categoria_sexo_bp.name = "categoria_sexo"  # El Blueprint que usaremos en `app.py`

@categoria_sexo_bp.route('/ver', endpoint='categoria_sexo_page')
def categoria_sexo_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        categorias_sexo = db.session.query(CategoriaSexo).filter(
            CategoriaSexo.nombre.ilike(f"%{query}%")
        ).all()
    else:
        categorias_sexo = db.session.query(CategoriaSexo).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('categoria_sexo.html', categorias_sexo=categorias_sexo, q=query)
#routes/administrador_routes.py
from flask import Blueprint, render_template

#Crear el Blueprint para Administrador
administrador_bp = Blueprint('administrador', __name__)

#Definir la ruta para la página de administrador
@administrador_bp.route('/ver/<documento>')
def administrador_page(documento):
    return render_template('administrador.html', documento=documento)
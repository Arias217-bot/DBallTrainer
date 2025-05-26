# routes/equipo_rival_routes.py
from routes.entidad_routes import EntidadRoutes
from models.equipo_rival import EquipoRival
from models.jugadores_rivales import JugadoresRivales
from models.torneo import Torneo
from flask import render_template, request, jsonify
from config import db
# Importar servicios para procesamiento automático
from services.extractor_service import (
    extract_text_from_image,
    extract_text_from_pdf,
    parse_text,
    save_to_database
)
import os

# Importar servicios para procesamiento automático
from services.extractor_service import (
    extract_text_from_image,
    extract_text_from_pdf,
    parse_text,
    save_to_database
)
import os

# Blueprints
equipo_rival_routes = EntidadRoutes('equipo_rival', EquipoRival)
equipo_rival_bp = equipo_rival_routes.bp
# Establecer el nombre del blueprint (se usa en app.py)
equipo_rival_bp.name = "equipo_rival"

@equipo_rival_bp.route('/ver', endpoint='equipo_rival_page')
def equipo_rival_page():
    query = request.args.get('q', '')
    if query:
        equipos_rivales = db.session.query(EquipoRival).filter(EquipoRival.nombre_equipo_rival.ilike(f"%{query}%")).all()
    else:
        equipos_rivales = db.session.query(EquipoRival).all()

    torneos = db.session.query(Torneo).all()
    return render_template('equipo_rival.html', equipos_rivales=equipos_rivales, torneos=torneos, q=query)
    
@equipo_rival_bp.route('/cargar-automatico', methods=['POST'])
def cargar_automatico_equipo_rival():
    """
    Endpoint para subir un archivo (PDF o imagen), extraer datos automáticamente
    y guardarlos en las tablas equipo_rival y jugadores_rivales.
    """
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    # Determinar extensión y preparar ruta temporal
    extension = os.path.splitext(archivo.filename)[1].lower()
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    ruta_temporal = os.path.join(upload_folder, archivo.filename)
    archivo.save(ruta_temporal)

    try:
        # Extraer texto según tipo de archivo
        if extension == '.pdf':
            texto = extract_text_from_pdf(ruta_temporal)
        else:
            texto = extract_text_from_image(ruta_temporal)

        # Parsear y guardar en base de datos
        equipo_data, jugadores_data = parse_text(texto)
        save_to_database(equipo_data, jugadores_data)

    except Exception as e:
        # 'Exception' es la clase base de errores en Python, no necesita import.
        # Aquí capturamos todos los errores que puedan ocurrir en el bloque try.
        return jsonify({'error': str(e)}), 500

    finally:
        # Limpiar archivo temporal
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)

    return jsonify({'mensaje': 'Equipo y jugadores cargados correctamente'}), 200

@equipo_rival_bp.route('/<nombre_torneo>/<nombre_equipo_rival>', endpoint='detalle_equipo_rival')
def detalle_equipo_rival(nombre_torneo, nombre_equipo_rival):
    nombre_torneo_formateado = nombre_torneo.replace("-", " ").lower()
    nombre_equipo_rival_formateado = nombre_equipo_rival.replace("-", " ").lower()

    # Buscar el torneo
    torneo = db.session.query(Torneo).filter(
        db.func.lower(Torneo.nombre_torneo) == nombre_torneo_formateado
    ).first()

    if not torneo:
        return "Torneo no encontrado", 404

    # Buscar el equipo rival
    equipo_rival = db.session.query(EquipoRival).filter(
        db.func.lower(EquipoRival.nombre_equipo_rival) == nombre_equipo_rival_formateado,
        EquipoRival.id_torneo == torneo.id_torneo
    ).first()

    if not equipo_rival:
        return "Equipo rival no encontrado", 404

    # Obtener los jugadores rivales del equipo
    jugadores_rivales = (
        db.session.query(JugadoresRivales)
        .filter(JugadoresRivales.nombre_equipo_rival == equipo_rival.nombre_equipo_rival)
        .all()
    )

    return render_template(
        'detalle_equipo_rival.html',
        equipo_rival=equipo_rival,
        torneo=torneo,
        nombre_torneo=nombre_torneo_formateado,
        nombre_equipo_rival=nombre_equipo_rival_formateado,
        jugadores_rivales=jugadores_rivales
    )
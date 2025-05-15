# routes/torneo_routes.py
from routes.entidad_routes import EntidadRoutes
from models.torneo import Torneo
from models.partido import Partido
from models.equipo_rival import EquipoRival

from flask import render_template, request
from config import db

# Blueprints
torneo_routes = EntidadRoutes('torneo', Torneo)
torneo_bp = torneo_routes.bp
torneo_bp.name = "torneo"  # El Blueprint que usaremos en `app.py`

@torneo_bp.route('/ver', endpoint='torneo_page')
def torneo_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        torneos = db.session.query(Torneo).filter(
            Torneo.nombre_torneo.ilike(f"%{query}%")
        ).all()
    else:
        torneos = db.session.query(Torneo).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('torneo.html', torneos=torneos, q=query)

@torneo_bp.route('/<nombre_equipo>/<id_torneo>/<nombre_torneo>', endpoint='detalle_torneo')
def detalle_torneo(id_torneo, nombre_equipo, nombre_torneo):
    # Buscar el equipo y torneo como ya lo haces
    nombre_equipo_formateado = nombre_equipo.replace("-", " ").lower()
    nombre_torneo_formateado = nombre_torneo.replace("-", " ").lower()

    equipo = db.session.query(Torneo.equipo.property.mapper.class_).filter(
        db.func.lower(Torneo.equipo.property.mapper.class_.nombre) == nombre_equipo_formateado
    ).first()

    if not equipo:
        return "Equipo no encontrado", 404

    torneo = db.session.query(Torneo).filter(
        db.func.lower(Torneo.nombre_torneo) == nombre_torneo_formateado,
        Torneo.id_equipo == equipo.id_equipo
    ).first()

    if not torneo:
        return "Torneo no encontrado", 404
    
    # Obtener partidos del torneo
    partidos = (
        db.session.query(Partido)
        .filter(Partido.id_torneo == torneo.id_torneo)
        .all()
    )

    partidos_lista = [
        {
            "nombre_partido": partido.nombre_partido,
            "nombre_equipo_rival": partido.nombre_equipo_rival,
            "fecha": partido.fecha.strftime('%Y-%m-%d %H:%M'),
            "lugar": partido.lugar or "Sin especificar",
            "marcador_local": partido.marcador_local,
            "marcador_rival": partido.marcador_rival,
            "video_url": partido.video_url or "Sin video",
            "observaciones": partido.observaciones or "Sin observaciones"
        }
        for partido in partidos
    ]

    # Obtener equipos rivales del torneo
    equipos_rivales = (
        db.session.query(EquipoRival)
        .filter(EquipoRival.id_torneo == torneo.id_torneo)
        .all()
    )

    equipos_rivales_lista = [
        {
            "nombre_equipo_rival": eq.nombre_equipo_rival,
            "categoria": eq.categoria,
            "director": eq.director,
            "asistente": eq.asistente,
            "director_cedula": eq.director_cedula,
            "asistente_cedula": eq.asistente_cedula
        }
        for eq in equipos_rivales
    ]

    # Aquí pasamos el documento del partido al contexto
    return render_template('detalle_torneo.html', torneo=torneo, equipo=equipo, id_torneo=id_torneo, partidos=partidos_lista, equipos_rivales=equipos_rivales_lista, nombre_equipo=nombre_equipo_formateado, nombre_torneo=nombre_torneo_formateado)

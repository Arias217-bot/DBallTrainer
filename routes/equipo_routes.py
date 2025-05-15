# routes/equipo_routes.py
from routes.entidad_routes import EntidadRoutes

from models.usuario import Usuario
from models.equipo import Equipo
from models.rol import Rol
from models.posicion import Posicion
from models.categoria_edad import CategoriaEdad
from models.categoria_sexo import CategoriaSexo
from models.usuario_equipo import Usuario_Equipo
from models.mensajes import Mensajes
from models.torneo import Torneo

from flask import render_template, request, jsonify
from config import db

# Blueprints
equipo_routes = EntidadRoutes('equipo', Equipo)
equipo_bp = equipo_routes.bp  # El Blueprint que usaremos en `app.py`

@equipo_bp.route('/ver/<documento>')
def perfil_equipos(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    equipos = (
        db.session.query(Equipo)
          .join(Usuario_Equipo, Usuario_Equipo.id_equipo == Equipo.id_equipo)
          .filter(Usuario_Equipo.documento == documento)
          .all()
    )

    categorias_edad = CategoriaEdad.query.all()
    categorias_sexo = CategoriaSexo.query.all()
    roles = Rol.query.all()               # <— Traigo todos los roles
    posiciones = Posicion.query.all()     # <— Traigo todas las posiciones

    return render_template(
        'equipos.html',
        usuario=usuario,
        equipos=[e.to_dict() for e in equipos],
        categorias_edad=categorias_edad,
        categorias_sexo=categorias_sexo,
        roles=roles,                       # <— Paso roles al template
        posiciones=posiciones,             # <— Paso posiciones al template
        documento=documento
    )

@equipo_bp.route('/<documento>/<nombre_equipo>')
def detalle_equipo(documento, nombre_equipo):

    # Obtener usuario
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    # Obtener todos los equipos del usuario
    equipos = (
        db.session.query(Equipo)
        .join(Usuario_Equipo, Usuario_Equipo.id_equipo == Equipo.id_equipo)
        .filter(Usuario_Equipo.documento == documento)
        .all()
    )

    # Buscar por nombre formateado
    equipo = next(
        (e for e in equipos if e.nombre.replace(" ", "-").lower() == nombre_equipo),
        None
    )
    if not equipo:
        return "Equipo no encontrado", 404

    # Obtener categorías
    categoria_edad = db.session.get(CategoriaEdad, equipo.id_categoria_edad)
    categoria_sexo = db.session.get(CategoriaSexo, equipo.id_categoria_sexo)

    # Obtener integrantes
    integrantes = (
        db.session.query(Usuario_Equipo, Usuario, Rol, Posicion, Usuario_Equipo.numero)
        .join(Usuario, Usuario.documento == Usuario_Equipo.documento)
        .outerjoin(Rol, Usuario_Equipo.id_rol == Rol.id_rol)
        .outerjoin(Posicion, Usuario_Equipo.id_posicion == Posicion.id_posicion)
        .filter(Usuario_Equipo.id_equipo == equipo.id_equipo)
        .all()
    )

    integrantes_lista = [
        {
            "id_usuario_equipo": usuario_equipo.id_usuario_equipo,
            "documento": usuario.documento,
            "nombre": usuario.nombre,
            "rol": rol.nombre if rol else "Sin rol",
            "posicion": posicion.nombre if posicion else "Sin posición",
            "numero": numero
        }
        for usuario_equipo, usuario, rol, posicion, numero in integrantes
    ]

    # Verificar mensajes con autor
    mensajes = (
        db.session.query(Mensajes, Usuario)
        .join(Usuario, Mensajes.autor == Usuario.documento)
        .filter(Mensajes.id_equipo == equipo.id_equipo)
        .order_by(Mensajes.fecha_envio.asc())
        .all()
    )

    mensajes_lista = [
        {
            "id_mensaje": mensaje.id_mensaje,
            "contenido": mensaje.contenido,
            "fecha_envio": mensaje.fecha_envio.strftime("%Y-%m-%d %H:%M:%S"),
            "autor": usuario.nombre
        }
        for mensaje, usuario in mensajes
    ]

    # Obtener torneos del equipo
    torneos = (
        db.session.query(Torneo)
        .filter(Torneo.id_equipo == equipo.id_equipo)
        .all()
    )

    torneos_lista = [
        {
            "id_torneo": torneo.id_torneo,
            "nombre_torneo": torneo.nombre_torneo,
            "descripcion": torneo.descripcion
        }
        for torneo in torneos
    ]

    # Obtener roles y posiciones
    roles = Rol.query.all()
    posiciones = Posicion.query.all()

    equipo_detalle = {
        "id_equipo": equipo.id_equipo,
        "nombre": equipo.nombre,
        "descripcion": equipo.descripcion,
        "categoria_edad": categoria_edad.nombre if categoria_edad else "Sin categoría",
        "categoria_sexo": categoria_sexo.nombre if categoria_sexo else "Sin categoría"
    }

    return render_template(
        'detalle_equipo.html',
        usuario=usuario,
        equipo=equipo_detalle,
        integrantes=integrantes_lista,
        roles=roles,
        posiciones=posiciones,
        documento=documento,
        mensajes=mensajes_lista,
        torneos=torneos_lista,
    )

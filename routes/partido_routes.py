from routes.entidad_routes import EntidadRoutes
from flask import render_template, request, jsonify
import re
from datetime import datetime, time
from config import db

# Modelos
from models.partido import Partido
from models.jugadas import Jugadas
from models.torneo import Torneo

# Blueprints
partido_routes = EntidadRoutes('partido', Partido)
partido_bp = partido_routes.bp  # El Blueprint que usaremos en `app.py`
partido_bp.name = "partido"

def calcular_duracion(tiempo_inicio, tiempo_fin):
    """
    Calcula la duración entre dos tiempos y devuelve un string formateado.
    Maneja tanto objetos time como strings en formato HH:MM:SS.
    """
    if not tiempo_inicio or not tiempo_fin:
        return ""
    
    # Convertir a objetos time si son strings
    if isinstance(tiempo_inicio, str):
        try:
            tiempo_inicio = datetime.strptime(tiempo_inicio, "%H:%M:%S").time()
        except ValueError:
            return "Formato inválido"
    
    if isinstance(tiempo_fin, str):
        try:
            tiempo_fin = datetime.strptime(tiempo_fin, "%H:%M:%S").time()
        except ValueError:
            return "Formato inválido"
    
    # Calcular diferencia en segundos
    inicio_segundos = tiempo_inicio.hour * 3600 + tiempo_inicio.minute * 60 + tiempo_inicio.second
    fin_segundos = tiempo_fin.hour * 3600 + tiempo_fin.minute * 60 + tiempo_fin.second
    
    duracion_segundos = fin_segundos - inicio_segundos
    if duracion_segundos < 0:
        duracion_segundos += 24 * 3600  # Manejar cambio de día
    
    minutos = duracion_segundos // 60
    segundos = duracion_segundos % 60
    
    return f"{minutos}m {segundos}s"

@partido_bp.route('/ver', methods=['GET'])
def partido_page():
    """Muestra la página con la lista de partidos, con opción de búsqueda."""
    query = request.args.get('q', '')
    if query:
        partidos_lista = db.session.query(Partido).filter(
            Partido.id_partido.like(f'%{query}%') 
        ).all()
    else:
        partidos_lista = db.session.query(Partido).all()
    return render_template('partido.html', partidos=partidos_lista, q=query)

@partido_bp.route('/<nombre_torneo>/<nombre_partido>', methods=['GET'])
def detalle_partido(nombre_torneo, nombre_partido):
    """Muestra el detalle de un partido específico con sus jugadas."""
    nombre_torneo = nombre_torneo.replace('-', ' ')
    nombre_partido = nombre_partido.replace('-', ' ')
    
    partido = Partido.query.filter_by(nombre_partido=nombre_partido).first_or_404()
    jugadas = Jugadas.query.filter_by(nombre_partido=nombre_partido).order_by(Jugadas._tiempo_inicio).all()
    
    return render_template('detalle_partido.html', 
                         partido=partido, 
                         jugadas=jugadas,
                         torneo_nombre=nombre_torneo,
                         calcular_duracion=calcular_duracion)

@partido_bp.route('/', methods=['POST'])
def create_jugada():
    """Crear una nueva jugada con procesamiento de la secuencia."""
    data = request.json
    secuencia = data.get('secuencia_jugada', '')
    
    # Procesar la secuencia para extraer datos estructurados
    pasos = []
    errores = []
    movimientos = secuencia.split(',')
    
    for i, movimiento in enumerate(movimientos):
        # Validar formato básico
        if not re.match(r'^j\d+[z\d++\-=]{1,2}$', movimiento):
            errores.append(f"Formato inválido en movimiento {i+1}: {movimiento}")
            continue
        
        # Extraer componentes
        jugador = re.search(r'j(\d+)', movimiento).group(1)
        accion = movimiento.replace(f'j{jugador}', '')
        
        paso = {
            'orden': i+1,
            'jugador': int(jugador),
            'tipo': 'zona' if accion.startswith('z') else 'accion',
            'valor': accion
        }
        
        if paso['tipo'] == 'zona':
            paso['zona'] = int(accion[1:])
        else:
            paso['evaluacion'] = {
                '++': 'excelente',
                '+': 'buena',
                '=': 'normal',
                '-': 'mala',
                '--': 'error'
            }.get(accion, 'desconocida')
        
        pasos.append(paso)
    
    if errores:
        return jsonify({'error': 'Errores en la secuencia', 'detalles': errores}), 400
    
    try:
        # Guardar tanto la secuencia original como los datos procesados
        nueva_jugada = Jugadas()
        data['datos_procesados'] = {'pasos': pasos}
        nueva_jugada.from_dict(data)
        
        db.session.add(nueva_jugada)
        db.session.commit()
        
        return jsonify(nueva_jugada.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al guardar la jugada', 'detalles': str(e)}), 500
    
@partido_bp.route('/estadisticas/<nombre_partido>', methods=['GET'])
def obtener_estadisticas(nombre_partido):
    # Obtener todas las jugadas del partido
    jugadas = Jugadas.query.filter_by(nombre_partido=nombre_partido).all()
    
    if not jugadas:
        return jsonify({'error': 'No hay jugadas registradas para este partido'}), 404
    
    estadisticas = {
        'rendimiento_jugadores': calcular_rendimiento_jugadores(jugadas),
        'distribucion_zonas': calcular_distribucion_zonas(jugadas),
        'efectividad_ataques': calcular_efectividad_ataques(jugadas),
        'comparativa_equipos': calcular_comparativa_equipos(jugadas)
    }
    
    return jsonify(estadisticas)

def calcular_rendimiento_jugadores(jugadas):
    rendimiento = {}
    for jugada in jugadas:
        if not jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso['tipo'] == 'accion':
                jugador = paso['jugador']
                accion = paso['accion']
                
                if jugador not in rendimiento:
                    rendimiento[jugador] = {
                        'excelentes': 0,
                        'buenas': 0,
                        'normales': 0,
                        'malas': 0,
                        'errores': 0,
                        'total_acciones': 0
                    }
                
                rendimiento[jugador]['total_acciones'] += 1
                
                if accion == '++':
                    rendimiento[jugador]['excelentes'] += 1
                elif accion == '+':
                    rendimiento[jugador]['buenas'] += 1
                elif accion == '=':
                    rendimiento[jugador]['normales'] += 1
                elif accion == '-':
                    rendimiento[jugador]['malas'] += 1
                elif accion == '--':
                    rendimiento[jugador]['errores'] += 1
    
    # Calcular porcentajes
    for jugador, stats in rendimiento.items():
        total = stats['total_acciones']
        if total > 0:
            stats['porcentaje_excelente'] = (stats['excelentes'] / total) * 100
            stats['porcentaje_efectivo'] = ((stats['excelentes'] + stats['buenas']) / total) * 100
            stats['porcentaje_error'] = (stats['errores'] / total) * 100
    
    return rendimiento

def calcular_distribucion_zonas(jugadas):
    zonas_ataque = {}
    for jugada in jugadas:
        if not jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso['tipo'] == 'zona' and paso['zona'] <= 6:  # Solo zonas de ataque
                zona = paso['zona']
                if zona not in zonas_ataque:
                    zonas_ataque[zona] = 0
                zonas_ataque[zona] += 1
    
    return zonas_ataque

def calcular_efectividad_ataques(jugadas):
    ataques = {'exitosos': 0, 'fallados': 0, 'total': 0}
    for jugada in jugadas:
        if not jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso['tipo'] == 'accion' and paso['accion'] in ['++', '+', '=', '-', '--']:
                ataques['total'] += 1
                if paso['accion'] in ['++', '+']:
                    ataques['exitosos'] += 1
                elif paso['accion'] == '--':
                    ataques['fallados'] += 1
    
    if ataques['total'] > 0:
        ataques['porcentaje_exitoso'] = (ataques['exitosos'] / ataques['total']) * 100
        ataques['porcentaje_fallado'] = (ataques['fallados'] / ataques['total']) * 100
    
    return ataques

def calcular_comparativa_equipos(jugadas):
    equipos = {'nuestro': 0, 'rival': 0, 'total': 0}
    for jugada in jugadas:
        if not jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso['tipo'] == 'accion':
                if paso['accion'] in ['++', '+']:
                    # Determinar si es nuestro equipo o el rival
                    for p in jugada.datos_procesados['pasos']:
                        if p['tipo'] == 'zona':
                            if p['zona'] <= 6:  # Nuestro equipo
                                equipos['nuestro'] += 1
                            else:  # Zonas del rival
                                equipos['rival'] += 1
                            equipos['total'] += 1
                            break
    
    if equipos['total'] > 0:
        equipos['porcentaje_nuestro'] = (equipos['nuestro'] / equipos['total']) * 100
        equipos['porcentaje_rival'] = (equipos['rival'] / equipos['total']) * 100
    
    return equipos
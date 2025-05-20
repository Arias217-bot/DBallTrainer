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

# Constantes para tipos de pasos
TIPO_ACCION = 'accion_completa'
TIPO_ZONA = 'zona'

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
    
    resumen_general = {
        'total_jugadas': len(jugadas),
        'acciones_totales': sum(len(j.datos_procesados.get('pasos', [])) for j in jugadas if j.datos_procesados)
    }

    return render_template('detalle_partido.html', 
                         partido=partido, 
                         jugadas=jugadas,
                         torneo_nombre=nombre_torneo,
                         resumen_general=resumen_general,
                         calcular_duracion=calcular_duracion)

@partido_bp.route('/procesar-jugada', methods=['POST'])
def create_jugada():
    """Crear una nueva jugada con procesamiento de la secuencia."""
    data = request.get_json()
    secuencia = data.get('secuencia_jugada', '')
    
    # Procesar la secuencia para extraer datos estructurados
    pasos = []
    errores = []
    movimientos = secuencia.split(',')
    
    for i, movimiento in enumerate(movimientos):
        # Expresión regular mejorada para capturar todos los componentes
        match = re.match(r'^j(\d+)(zr?\d+)(\w+)([\+\-\=]{1,2})$', movimiento.strip())
        if not match:
            errores.append(f"Formato inválido en movimiento {i+1}: {movimiento}")
            continue
        
        jugador, zona, tipo_accion, evaluacion = match.groups()
        
        pasos.append({
            'orden': i+1,
            'tipo': TIPO_ACCION,
            'jugador': f"j{jugador}",
            'zona': zona,
            'tipoAccion': tipo_accion,
            'evaluacion': evaluacion
        })
    
    if errores:
        return jsonify({'error': 'Errores en la secuencia', 'detalles': errores}), 400
    
    try:
        # Crear nueva jugada
        nueva_jugada = Jugadas()
        
        # Asignar valores básicos
        nueva_jugada.nombre_partido = data.get('nombre_partido')
        nueva_jugada.secuencia_jugada = secuencia
        
        # Manejar tiempos (usando los setters de la propiedad)
        if 'tiempo_inicio' in data:
            nueva_jugada.tiempo_inicio = datetime.strptime(data['tiempo_inicio'], '%H:%M:%S').time()
        if 'tiempo_fin' in data:
            nueva_jugada.tiempo_fin = datetime.strptime(data['tiempo_fin'], '%H:%M:%S').time()
        
        # Asignar datos procesados directamente como diccionario
        nueva_jugada.datos_procesados = {'pasos': pasos}
        
        db.session.add(nueva_jugada)
        db.session.commit()
        
        return jsonify({
            'id_jugada': nueva_jugada.id_jugada,
            'nombre_partido': nueva_jugada.nombre_partido,
            'secuencia_jugada': nueva_jugada.secuencia_jugada,
            'tiempo_inicio': str(nueva_jugada.tiempo_inicio) if nueva_jugada.tiempo_inicio else None,
            'tiempo_fin': str(nueva_jugada.tiempo_fin) if nueva_jugada.tiempo_fin else None,
            'datos_procesados': nueva_jugada.datos_procesados
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al guardar la jugada', 'detalles': str(e)}), 500

@partido_bp.route('/<nombre_partido>/estadisticas', methods=['GET'])
def obtener_estadisticas(nombre_partido):
    nombre_partido = nombre_partido.replace('-', ' ')
    """Obtiene todas las estadísticas del partido."""
    # Obtener todas las jugadas del partido
    jugadas = Jugadas.query.filter_by(nombre_partido=nombre_partido).all()
    
    if not jugadas:
        return jsonify({'error': 'No hay jugadas registradas para este partido'}), 404
    
    # Verificar formato de datos para depuración
    for jugada in jugadas:
        print(f"Jugada ID: {jugada.id_jugada}")
        print(f"Datos procesados: {jugada.datos_procesados}")
    
    estadisticas = {
        'resumen_general': calcular_resumen_general(jugadas),
        'rendimiento_jugadores': calcular_rendimiento_jugadores(jugadas),
        'distribucion_zonas': calcular_distribucion_zonas(jugadas),
        'efectividad_por_tipo': calcular_efectividad_por_tipo(jugadas),
        'comparativa_equipos': calcular_comparativa_equipos(jugadas),
        'secuencias_comunes': identificar_secuencias_comunes(jugadas)
    }
    
    return jsonify(estadisticas)

def calcular_resumen_general(jugadas):
    resumen = {
        'total_jugadas': len(jugadas),
        'acciones_totales': 0,
        'excelentes': 0,
        'buenas': 0,
        'normales': 0,
        'malas': 0,
        'errores': 0
    }
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso.get('tipo') == TIPO_ACCION:
                resumen['acciones_totales'] += 1
                evaluacion = paso.get('evaluacion', '')
                
                if evaluacion == '++':
                    resumen['excelentes'] += 1
                elif evaluacion == '+':
                    resumen['buenas'] += 1
                elif evaluacion == '=':
                    resumen['normales'] += 1
                elif evaluacion == '-':
                    resumen['malas'] += 1
                elif evaluacion == '--':
                    resumen['errores'] += 1
    
    # Calcular porcentajes
    if resumen['acciones_totales'] > 0:
        resumen['porcentaje_excelente'] = round((resumen['excelentes'] / resumen['acciones_totales']) * 100, 2)
        resumen['porcentaje_efectivo'] = round(((resumen['excelentes'] + resumen['buenas']) / resumen['acciones_totales']) * 100, 2)
        resumen['porcentaje_error'] = round((resumen['errores'] / resumen['acciones_totales']) * 100, 2)
    
    return resumen

def calcular_rendimiento_jugadores(jugadas):
    rendimiento = {}
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso.get('tipo') == TIPO_ACCION:
                jugador = paso.get('jugador', '')
                evaluacion = paso.get('evaluacion', '')
                
                if not jugador:
                    continue
                    
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
                
                if evaluacion == '++':
                    rendimiento[jugador]['excelentes'] += 1
                elif evaluacion == '+':
                    rendimiento[jugador]['buenas'] += 1
                elif evaluacion == '=':
                    rendimiento[jugador]['normales'] += 1
                elif evaluacion == '-':
                    rendimiento[jugador]['malas'] += 1
                elif evaluacion == '--':
                    rendimiento[jugador]['errores'] += 1
    
    # Calcular porcentajes para cada jugador
    for jugador, stats in rendimiento.items():
        if stats['total_acciones'] > 0:
            stats['porcentaje_excelente'] = round((stats['excelentes'] / stats['total_acciones']) * 100, 2)
            stats['porcentaje_efectivo'] = round(((stats['excelentes'] + stats['buenas']) / stats['total_acciones']) * 100, 2)
            stats['porcentaje_error'] = round((stats['errores'] / stats['total_acciones']) * 100, 2)
    
    return rendimiento

def calcular_distribucion_zonas(jugadas):
    zonas = {}
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso.get('tipo') == TIPO_ACCION:
                zona = paso.get('zona', '')
                if zona:
                    if zona not in zonas:
                        zonas[zona] = 0
                    zonas[zona] += 1
    
    return zonas

def calcular_efectividad_por_tipo(jugadas):
    tipos_accion = {
        'saque': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0},
        'recibo': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0},
        'pase': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0},
        'remate': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0},
        'bloqueo': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0},
        'defensa': {'total': 0, 'exitosos': 0, 'normales': 0, 'fallados': 0}
    }
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso.get('tipo') == TIPO_ACCION:
                tipo_accion = paso.get('tipoAccion', '').lower()
                evaluacion = paso.get('evaluacion', '')
                
                if tipo_accion in tipos_accion:
                    tipos_accion[tipo_accion]['total'] += 1
                    
                    if evaluacion in ['++', '+']:
                        tipos_accion[tipo_accion]['exitosos'] += 1
                    elif evaluacion == '=':
                        tipos_accion[tipo_accion]['normales'] += 1
                    elif evaluacion in ['-', '--']:
                        tipos_accion[tipo_accion]['fallados'] += 1
    
    # Calcular porcentajes para cada tipo de acción
    for tipo, datos in tipos_accion.items():
        if datos['total'] > 0:
            datos['porcentaje_exitoso'] = round((datos['exitosos'] / datos['total']) * 100, 2)
            datos['porcentaje_normal'] = round((datos['normales'] / datos['total']) * 100, 2)
            datos['porcentaje_fallado'] = round((datos['fallados'] / datos['total']) * 100, 2)
    
    return tipos_accion

def calcular_comparativa_equipos(jugadas):
    equipos = {
        'nuestro': {'excelentes': 0, 'buenas': 0, 'normales': 0, 'malas': 0, 'errores': 0, 'total': 0},
        'rival': {'excelentes': 0, 'buenas': 0, 'normales': 0, 'malas': 0, 'errores': 0, 'total': 0}
    }
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        for paso in jugada.datos_procesados['pasos']:
            if paso.get('tipo') == TIPO_ACCION:
                jugador = paso.get('jugador', '')
                evaluacion = paso.get('evaluacion', '')
                
                # Determinar equipo basado en el número de jugador
                try:
                    num_jugador = int(jugador.replace('j', ''))
                    equipo = 'nuestro' if 1 <= num_jugador <= 6 else 'rival'
                except:
                    continue
                
                equipos[equipo]['total'] += 1
                
                if evaluacion == '++':
                    equipos[equipo]['excelentes'] += 1
                elif evaluacion == '+':
                    equipos[equipo]['buenas'] += 1
                elif evaluacion == '=':
                    equipos[equipo]['normales'] += 1
                elif evaluacion == '-':
                    equipos[equipo]['malas'] += 1
                elif evaluacion == '--':
                    equipos[equipo]['errores'] += 1
    
    # Calcular porcentajes para cada equipo
    for equipo, stats in equipos.items():
        if stats['total'] > 0:
            stats['porcentaje_excelente'] = round((stats['excelentes'] / stats['total']) * 100, 2)
            stats['porcentaje_efectivo'] = round(((stats['excelentes'] + stats['buenas']) / stats['total']) * 100, 2)
            stats['porcentaje_error'] = round((stats['errores'] / stats['total']) * 100, 2)
    
    return equipos

def identificar_secuencias_comunes(jugadas, min_repeticiones=2):
    secuencias = {}
    
    for jugada in jugadas:
        if not jugada.datos_procesados or 'pasos' not in jugada.datos_procesados:
            continue
            
        pasos = jugada.datos_procesados.get('pasos', [])
        if len(pasos) < 3:  # Solo considerar secuencias de al menos 3 pasos
            continue
            
        # Crear clave de secuencia (ej: "saque->pase->remate")
        clave_secuencia = '->'.join(
            f"{p.get('tipoAccion', '')}:{p.get('evaluacion', '')}" 
            for p in pasos if p.get('tipo') == TIPO_ACCION
        )
        
        if clave_secuencia:
            secuencias[clave_secuencia] = secuencias.get(clave_secuencia, 0) + 1
    
    # Filtrar solo secuencias repetidas y ordenar por frecuencia
    secuencias_filtradas = {k: v for k, v in secuencias.items() if v >= min_repeticiones}
    return dict(sorted(secuencias_filtradas.items(), key=lambda item: item[1], reverse=True))
# routes/videos_routes.py
import os
import json
from flask import render_template, request, current_app, url_for, jsonify, abort, send_file
import pandas as pd
from io import BytesIO
from werkzeug.utils import secure_filename
import cv2
import mediapipe as mp
from datetime import datetime

from integration import analizar_video
from models.usuario import Usuario
from models.deteccion import Deteccion
from models.modalidad import Modalidad
from models.videos import Videos
from config import db
from routes.entidad_routes import EntidadRoutes

# Extensiones permitidas para videos
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Creamos el Blueprint y las rutas genéricas
videos_routes = EntidadRoutes('videos', Videos)
videos_bp = videos_routes.bp
videos_bp.name = "videos"

@videos_bp.route('/upload', methods=['POST'])
def upload_video():
    """Endpoint para subir videos sin procesamiento automático"""
    nombre = request.form.get('nombre')
    file = request.files.get('video_file')
    documento = request.form.get('documento')
    id_modalidad = request.form.get('id_modalidad')
    id_deteccion = request.form.get('id_deteccion')

    # Validaciones
    if not nombre or not file or not allowed_file(file.filename):
        return jsonify({'error': 'Datos inválidos o formato no permitido'}), 400
    
    modalidad = Modalidad.query.get(id_modalidad)
    deteccion = Deteccion.query.get(id_deteccion)
    
    if not modalidad or not deteccion:
        return jsonify({'error': 'Modalidad o detección no válidas'}), 400

    # Guardar archivo
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, filename))

    # Crear registro en BD
    nuevo_video = Videos(
        nombre=nombre, 
        url=url_for('static', filename=f'uploads/{filename}'), 
        documento_usuario=documento,
        id_modalidad=id_modalidad, 
        id_deteccion=id_deteccion
    )
    db.session.add(nuevo_video)
    db.session.commit()

    return jsonify(nuevo_video.to_dict()), 201

@videos_bp.route('/ver/<documento>')
def videos_usuario(documento):
    """Listar videos de un usuario sin procesamiento automático"""
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    videos = (Videos.query
              .join(Usuario, Videos.documento_usuario == Usuario.documento)
              .filter(Usuario.documento == documento)
              .all())

    return render_template(
        'mis_videos.html',
        usuario=usuario,
        videos=[v.to_dict() for v in videos],
        modalidades=Modalidad.query.all(),
        detecciones=Deteccion.query.all(),
        documento=documento
    )

@videos_bp.route('/ver/<documento>/<nombre>')
def detalle_video(documento, nombre):
    """Mostrar detalles de un video específico"""
    nombre_normalizado = nombre.replace('-', ' ').lower()
    video = Videos.query.filter(
        Videos.documento_usuario == documento,
        db.func.lower(Videos.nombre) == nombre_normalizado
    ).first_or_404()

    return render_template('detalle_video.html', video=video)

@videos_bp.route('/ver/<documento>/analizar/<int:id_video>', methods=['POST'])
def analizar_video_usuario(documento, id_video):
    """Analizar un video específico"""
    try:
        video = Videos.query.filter_by(id_video=id_video, documento_usuario=documento).first_or_404()
        
        if not video.url:
            return jsonify({"status": "error", "message": "El video no tiene URL válida"}), 400

        # Obtener ruta física del video
        video_path = os.path.join(current_app.root_path, 'static', video.url.replace('/static/', ''))
        if not os.path.exists(video_path):
            return jsonify({"status": "error", "message": "El archivo de video no existe"}), 404

        # Obtener configuración de detección
        deteccion = Deteccion.query.get(video.id_deteccion)
        if not deteccion:
            return jsonify({"status": "error", "message": "Tipo de detección no configurado"}), 400

        # Realizar análisis (aquí llamarías a tu función de análisis)
        resultados = analizar_video(video_path, deteccion.nombre)
        if not resultados:
            raise ValueError("El análisis no devolvió resultados")

        # Procesar y guardar resultados
        stats = {
            'total_frames': len(resultados),
            'frames_con_deteccion': sum(1 for r in resultados if r.get('resultados_deteccion')),
            'porcentaje': f"{sum(1 for r in resultados if r.get('resultados_deteccion')) / len(resultados) * 100:.2f}%",
            'tipo_deteccion': deteccion.nombre,
            'fecha_analisis': datetime.now().isoformat()
        }

        video.resultados_analisis = {'datos_brutos': resultados, 'estadisticas': stats}
        db.session.commit()

        return jsonify({"status": "success", "stats": stats, "id_video": video.id_video})

    except Exception as e:
        current_app.logger.error(f"Error en análisis: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@videos_bp.route('/procesado/<int:id_video>', methods=['GET'])
def get_processed_video(id_video):
    """Generar y servir el video con landmarks"""
    video = Videos.query.get_or_404(id_video)

    # Rutas
    original_path = os.path.join(current_app.root_path, 'static', video.url.replace('/static/', ''))
    processed_dir = os.path.join(current_app.root_path, 'static', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    processed_path = os.path.join(processed_dir, f'processed_{id_video}.mp4')

    if os.path.exists(processed_path):
        try:
            os.remove(processed_path)
        except Exception as e:
            current_app.logger.error(f"Error eliminando video previo: {str(e)}")

    cap = cv2.VideoCapture(original_path)
    if not cap.isOpened():
        abort(500, description="No se pudo abrir el video original")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Intentar varios códecs
    codecs_to_try = ['mp4v', 'avc1', 'XVID']
    writer_ok = False

    for codec in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(processed_path, fourcc, fps, (width, height))
            if out.isOpened():
                writer_ok = True
                break
        except Exception as e:
            current_app.logger.warning(f"No se pudo usar codec {codec}: {e}")

    if not writer_ok:
        cap.release()
        abort(500, description="No se pudo inicializar VideoWriter con ningún codec válido")

    # MediaPipe config
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=1)
                )

            out.write(frame)

        out.release()
        cap.release()
        pose.close()

        if not os.path.exists(processed_path) or os.path.getsize(processed_path) == 0:
            raise ValueError("El archivo de video generado está vacío")

        return send_file(
            processed_path,
            mimetype='video/mp4',
            as_attachment=False,  # Si prefieres que lo descargue, pon True
            download_name=f"video_procesado_{id_video}.mp4"
        )

    except Exception as e:
        current_app.logger.error(f"Error al procesar video: {str(e)}")
        abort(500, description=f"Error al generar el video procesado: {str(e)}")

@videos_bp.route('/ver/<documento>/reporte/<int:id_video>', methods=['GET'])
def generar_reporte(documento, id_video):
    """Generar reporte en Excel con los resultados"""
    try:
        video = Videos.query.filter_by(id_video=id_video, documento_usuario=documento).first_or_404()

        if not video.resultados_analisis:
            return jsonify({"error": "El video no ha sido analizado"}), 400

        # Procesar datos para el reporte
        datos_brutos = video.resultados_analisis.get('datos_brutos', [])
        df = pd.DataFrame(datos_brutos)
        
        # Estadísticas
        stats = {
            'total_frames': len(datos_brutos),
            'frames_con_deteccion': sum(1 for r in datos_brutos if r.get('resultados_deteccion')),
            'porcentaje_deteccion': f"{sum(1 for r in datos_brutos if r.get('resultados_deteccion')) / len(datos_brutos) * 100:.2f}%",
            'frames_con_contacto': sum(1 for r in datos_brutos if r.get('contacto')),
            'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo_deteccion': video.deteccion.nombre,
            'modelo_utilizado': "MediaPipe v0.9"
        }

        # Crear Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Datos Brutos', index=False)
            pd.DataFrame.from_dict(stats, orient='index', columns=['Valor'])\
                .to_excel(writer, sheet_name='Resumen')

        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"reporte_{video.nombre}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        current_app.logger.error(f"Error generando reporte: {str(e)}")
        return jsonify({"error": str(e)}), 500
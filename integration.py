# Importación de librerías necesarias
import cv2
import mediapipe as mp
import pandas as pd
import os
import math
import logging
from datetime import datetime
from pathlib import Path
import json
from evaluaciones.evaluar_contacto import evaluar_contacto

# Importar funciones de detección específicas
from detecciones import (
    detectar_saque, obtener_encabezados_saque,
    detectar_colocador, obtener_encabezados_colocador,
    detectar_ataque, obtener_encabezados_ataque,
    detectar_recibo, obtener_encabezados_recibo,
    detectar_bloqueo, obtener_encabezados_bloqueo
)

# Configuración de logs
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, 
                    format="%(asctime)s - %(message)s")

# Inicializar soluciones de MediaPipe con configuración robusta
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Configuración robusta para el modelo de pose
def create_pose_instance():
    """Crea una instancia de Pose con configuración robusta"""
    return mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

def analizar_video(video_path, deteccion):
    """
    Versión robusta para análisis de video con manejo mejorado de timestamps
    """
    if deteccion not in funciones_deteccion:
        logging.error(f"Detección no válida: {deteccion}")
        print(f"Error: Detección no válida: {deteccion}")
        return None

    detectar_func, _ = funciones_deteccion[deteccion]
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"No se pudo abrir el video en: {video_path}")
        print(f"Error: No se pudo abrir el video en: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    resultados = []
    frame_number = 0
    pose = create_pose_instance()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Manejo de frames corruptos
            if frame is None or frame.size == 0:
                logging.warning(f"Frame {frame_number} corrupto - omitiendo")
                frame_number += 1
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            try:
                # Solución alternativa para el problema de timestamps:
                # 1. Procesar el frame directamente
                # 2. Si falla, recrear la instancia de pose y reintentar
                results = pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    landmarks = list(results.pose_landmarks.landmark)
                    evaluacion_resultados = detectar_func(landmarks)
                    hay_contacto = evaluar_contacto(landmarks)

                    resultados.append({
                        "frame": frame_number,
                        "timestamp": frame_number / fps,
                        "deteccion": deteccion,
                        "resultados_deteccion": evaluacion_resultados,
                        "contacto": hay_contacto,
                        "landmarks": {
                            mp_pose.PoseLandmark(i).name: {
                                "x": lm.x,
                                "y": lm.y, 
                                "z": lm.z,
                                "visibility": lm.visibility
                            } for i, lm in enumerate(landmarks)
                        }
                    })

            except Exception as e:
                logging.error(f"Error procesando frame {frame_number}: {str(e)}")
                # Recrear la instancia de pose si hay error
                pose.close()
                pose = create_pose_instance()
                continue

            frame_number += 1

    except Exception as e:
        logging.error(f"Error durante el procesamiento del video: {str(e)}")
        raise
    finally:
        cap.release()
        pose.close()
    
    return resultados if resultados else None

def analizar_video(video_path, deteccion, pose_instance=None):
    """
    Versión mejorada con manejo robusto de timestamps y frames
    """
    if deteccion not in funciones_deteccion:
        logging.error(f"Detección no válida: {deteccion}")
        print(f"Error: Detección no válida: {deteccion}")
        return None

    detectar_func, _ = funciones_deteccion[deteccion]
    
    # Usar la instancia proporcionada o crear una nueva
    pose = pose_instance if pose_instance else create_pose_instance()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"No se pudo abrir el video en: {video_path}")
        print(f"Error: No se pudo abrir el video en: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    resultados = []
    frame_number = 0
    last_timestamp = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Manejo robusto de frames corruptos
            if frame is None or frame.size == 0:
                logging.warning(f"Frame {frame_number} corrupto - omitiendo")
                frame_number += 1
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Asignar timestamp consistente
            current_timestamp = int(frame_number * 1e6)  # Microsegundos
            if current_timestamp <= last_timestamp:
                current_timestamp = last_timestamp + 1
            
            try:
                results = pose.process(frame_rgb)
                last_timestamp = current_timestamp
                
                if results.pose_landmarks:
                    landmarks = list(results.pose_landmarks.landmark)
                    evaluacion_resultados = detectar_func(landmarks)
                    hay_contacto = evaluar_contacto(landmarks)

                    resultados.append({
                        "frame": frame_number,
                        "timestamp": frame_number / fps,
                        "deteccion": deteccion,
                        "resultados_deteccion": evaluacion_resultados,
                        "contacto": hay_contacto,
                        "landmarks": {
                            mp_pose.PoseLandmark(i).name: {
                                "x": lm.x,
                                "y": lm.y, 
                                "z": lm.z,
                                "visibility": lm.visibility
                            } for i, lm in enumerate(landmarks)
                        }
                    })

            except Exception as e:
                logging.error(f"Error procesando frame {frame_number}: {str(e)}")
                # Recrear la instancia de pose si hay error
                pose = create_pose_instance()
                continue

            frame_number += 1

    finally:
        cap.release()
        if not pose_instance:  # Solo cerrar si lo creamos nosotros
            pose.close()
    
    return resultados if resultados else None

def analizar_camara(deteccion):
    """
    Versión robusta para análisis de cámara
    """
    if deteccion not in funciones_deteccion:
        logging.error(f"Detección no válida: {deteccion}")
        print(f"Error: Detección no válida: {deteccion}")
        return None

    detectar_func, _ = funciones_deteccion[deteccion]
    pose = create_pose_instance()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("No se pudo abrir la cámara.")
        print("Error: No se pudo abrir la cámara.")
        return None

    resultados_json = []
    frame_number = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.warning("Frame de cámara no recibido - reintentando")
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            try:
                results = pose.process(frame_rgb)

                if results.pose_landmarks:
                    landmarks = list(results.pose_landmarks.landmark)
                    evaluacion_resultados = detectar_func(landmarks)
                    hay_contacto = evaluar_contacto(landmarks)

                    resultados_json.append({
                        "frame": frame_number,
                        "timestamp": datetime.now().isoformat(),
                        "deteccion": deteccion,
                        "resultados_deteccion": evaluacion_resultados,
                        "contacto": hay_contacto,
                        "landmarks": [(lm.x, lm.y, lm.z, lm.visibility) for lm in landmarks]
                    })

            except Exception as e:
                logging.error(f"Error procesando frame de cámara: {str(e)}")
                pose = create_pose_instance()  # Reiniciar instancia
                continue

            frame_number += 1

    except KeyboardInterrupt:
        print("\nAnálisis detenido por el usuario")
    finally:
        cap.release()
        pose.close()
        cv2.destroyAllWindows()
    
    return resultados_json

# Mapeo de funciones de detección
funciones_deteccion = {
    "Saque": (detectar_saque, obtener_encabezados_saque),
    "Colocador": (detectar_colocador, obtener_encabezados_colocador),
    "Ataque": (detectar_ataque, obtener_encabezados_ataque),
    "Recibo": (detectar_recibo, obtener_encabezados_recibo),
    "Bloqueo": (detectar_bloqueo, obtener_encabezados_bloqueo),
}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Script para análisis de voleibol (una persona) para API")
    parser.add_argument('--fuente', type=str, choices=['camara', 'video'], default='video', help='Fuente del video')
    parser.add_argument('--ruta_video', type=str, help='Ruta al archivo de video si la fuente es "video"')
    parser.add_argument('--deteccion', type=str, choices=list(funciones_deteccion.keys()), required=True, help='Acción a detectar')
    args = parser.parse_args()

    try:
        if args.fuente == 'video':
            if args.ruta_video:
                resultados = analizar_video_con_reintentos(args.ruta_video, args.deteccion)
                if resultados:
                    print(json.dumps(resultados, indent=4))
            else:
                print("Error: Debes especificar la ruta del video con --ruta_video.")
        elif args.fuente == 'camara':
            print(f"Iniciando análisis de la cámara para '{args.deteccion}'. Presiona Ctrl+C para detener.")
            resultados = analizar_camara(args.deteccion)
            if resultados:
                print(json.dumps(resultados, indent=4))
    except Exception as e:
        logging.error(f"Error fatal: {str(e)}")
        print(f"Error crítico: {str(e)}")
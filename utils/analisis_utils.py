# analysis_utils.py
import math
import logging
import mediapipe as mp
from typing import Dict, List, Tuple

# Inicializar soluciones de MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calcular_angulos(landmarks: List[mp_pose.PoseLandmark]) -> Dict[str, float]:
    """
    Calcula ángulos clave entre puntos del cuerpo usando MediaPipe PoseLandmark.
    
    Args:
        landmarks: Lista de landmarks de pose de MediaPipe
    
    Returns:
        Diccionario con los ángulos calculados y sus valores en grados
    """
    if not landmarks or len(landmarks) < 33:  # MediaPipe Pose tiene 33 landmarks
        logger.warning("Landmarks incompletos para calcular ángulos")
        return {}
    
    try:
        # Convertir landmarks a diccionario para fácil acceso
        landmark_dict = {
            mp_pose.PoseLandmark(i).name: landmarks[i] 
            for i in range(len(landmarks))
        }
        
        angulos = {
            'angulo_codo_izquierdo': calcular_angulo_3_puntos(
                landmark_dict['LEFT_SHOULDER'],
                landmark_dict['LEFT_ELBOW'],
                landmark_dict['LEFT_WRIST']
            ),
            'angulo_codo_derecho': calcular_angulo_3_puntos(
                landmark_dict['RIGHT_SHOULDER'],
                landmark_dict['RIGHT_ELBOW'],
                landmark_dict['RIGHT_WRIST']
            ),
            'angulo_hombro_izquierdo': calcular_angulo_3_puntos(
                landmark_dict['LEFT_ELBOW'],
                landmark_dict['LEFT_SHOULDER'],
                landmark_dict['LEFT_HIP']
            ),
            'angulo_hombro_derecho': calcular_angulo_3_puntos(
                landmark_dict['RIGHT_ELBOW'],
                landmark_dict['RIGHT_SHOULDER'],
                landmark_dict['RIGHT_HIP']
            ),
            'angulo_rodilla_izquierda': calcular_angulo_3_puntos(
                landmark_dict['LEFT_HIP'],
                landmark_dict['LEFT_KNEE'],
                landmark_dict['LEFT_ANKLE']
            ),
            'angulo_rodilla_derecha': calcular_angulo_3_puntos(
                landmark_dict['RIGHT_HIP'],
                landmark_dict['RIGHT_KNEE'],
                landmark_dict['RIGHT_ANKLE']
            )
        }
        
        return angulos
    
    except Exception as e:
        logger.error(f"Error calculando ángulos: {str(e)}")
        return {}

def calcular_angulo_3_puntos(
    a: mp_pose.PoseLandmark, 
    b: mp_pose.PoseLandmark, 
    c: mp_pose.PoseLandmark
) -> float:
    """
    Calcula el ángulo ABC formado por tres landmarks de MediaPipe.
    
    Args:
        a, b, c: Landmarks de MediaPipe (deben tener atributos x, y)
    
    Returns:
        Ángulo en grados entre los puntos a-b-c
    """
    try:
        # Vectores BA y BC
        ba_x = a.x - b.x
        ba_y = a.y - b.y
        bc_x = c.x - b.x
        bc_y = c.y - b.y
        
        # Producto punto y magnitudes
        dot_product = ba_x * bc_x + ba_y * bc_y
        mag_ba = math.sqrt(ba_x**2 + ba_y**2)
        mag_bc = math.sqrt(bc_x**2 + bc_y**2)
        
        # Evitar división por cero
        if mag_ba == 0 or mag_bc == 0:
            return 0.0
            
        # Calcular ángulo en radianes y convertir a grados
        angle_rad = math.acos(min(max(dot_product / (mag_ba * mag_bc), -1.0), 1.0))
        return math.degrees(angle_rad)
        
    except Exception as e:
        logger.error(f"Error calculando ángulo: {str(e)}")
        return 0.0

def obtener_nombres_landmarks() -> List[str]:
    """Devuelve los nombres de todos los landmarks de MediaPipe Pose"""
    return [landmark.name for landmark in mp_pose.PoseLandmark]

def dibujar_angulos_en_imagen(
    image, 
    landmarks: List[mp_pose.PoseLandmark],
    angulos: Dict[str, float]
) -> None:
    """
    Dibuja los ángulos calculados sobre la imagen.
    
    Args:
        image: Imagen OpenCV donde dibujar
        landmarks: Lista de landmarks de pose
        angulos: Diccionario de ángulos a mostrar
    """
    try:
        # Dibujar landmarks y conexiones
        mp_drawing.draw_landmarks(
            image,
            mp_pose.PoseLandmark(landmarks),
            mp_pose.POSE_CONNECTIONS
        )
        
        # Configuración de texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)  # Blanco
        thickness = 1
        
        # Posición inicial para mostrar ángulos
        text_y = 30
        
        # Mostrar cada ángulo en la imagen
        for nombre, valor in angulos.items():
            text = f"{nombre}: {valor:.1f}°"
            cv2.putText(image, text, (10, text_y), font, font_scale, color, thickness)
            text_y += 20
            
    except Exception as e:
        logger.error(f"Error dibujando ángulos: {str(e)}")
import mediapipe as mp
from typing import List, Dict, Union

mp_pose = mp.solutions.pose

def validar_landmarks(landmarks: Dict, indices: List[int]) -> bool:
    """
    Valida que los landmarks sean un diccionario y contengan los índices necesarios.
    Args:
        landmarks (dict): Diccionario de puntos de referencia detectados.
        indices (list): Índices de landmarks requeridos.
    Returns:
        bool: True si los landmarks son válidos, False en caso contrario.
    """
    if not isinstance(landmarks, dict) or not all(idx in landmarks for idx in indices):
        return False
    return True

def evaluar_posicion(
    landmarks: Dict,
    umbral_altura: float = 0.1
) -> Dict[str, Union[str, bool, Dict[str, float]]]:
    """
    Evalúa la posición inicial basada en los puntos de referencia del cuerpo.
    Args:
        landmarks (dict): Diccionario de puntos de referencia detectados por MediaPipe.
        umbral_altura (float): Tolerancia para evaluar la alineación vertical.
    Returns:
        dict: Resultado de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar landmarks
        indices_necesarios = [
            mp_pose.PoseLandmark.LEFT_SHOULDER.value,
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
            mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value,
            mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value
        ]
        if not validar_landmarks(landmarks, indices_necesarios):
            raise ValueError("Landmarks inválidos o incompletos.")

        # Obtener los landmarks necesarios
        hombro_izq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hombro_der = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        pie_izq = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
        pie_der = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]

        # Evaluar alineación vertical (hombros por encima de los pies)
        hombro_izq_correcto = hombro_izq.y < pie_izq.y - umbral_altura
        hombro_der_correcto = hombro_der.y < pie_der.y - umbral_altura

        # Evaluar postura general
        postura_correcta = hombro_izq_correcto and hombro_der_correcto

        # Formatear resultados
        mensaje = (
            "Posición inicial correcta" if postura_correcta
            else "Ajustar posición inicial: hombros deben estar por encima de los pies."
        )
        datos = {
            "hombro_izq_y": hombro_izq.y,
            "hombro_der_y": hombro_der.y,
            "pie_izq_y": pie_izq.y,
            "pie_der_y": pie_der.y,
            "hombro_izq_correcto": hombro_izq_correcto,
            "hombro_der_correcto": hombro_der_correcto
        }

        return {"mensaje": mensaje, "postura_correcta": postura_correcta, "datos": datos}

    except Exception as e:
        return {"mensaje": f"Error en la evaluación: {e}", "postura_correcta": False, "datos": {}}
import mediapipe as mp
from typing import Dict, Union, List

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

def evaluar_movimiento(
    landmarks: Dict,
    umbral: float = 0.1
) -> Dict[str, Union[str, bool, Dict[str, float]]]:
    """
    Evalúa el movimiento de preparación basado en los landmarks proporcionados.
    Args:
        landmarks (dict): Diccionario de puntos de referencia detectados por MediaPipe.
        umbral (float): Tolerancia para evaluar la alineación vertical.
    Returns:
        dict: Resultado de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar landmarks
        indices_necesarios = [
            mp_pose.PoseLandmark.LEFT_HIP.value,
            mp_pose.PoseLandmark.RIGHT_HIP.value,
            mp_pose.PoseLandmark.LEFT_SHOULDER.value,
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value
        ]
        if not validar_landmarks(landmarks, indices_necesarios):
            raise ValueError("Landmarks inválidos o incompletos.")

        # Obtener los landmarks necesarios
        cadera_izq = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        cadera_der = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        hombro_izq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        hombro_der = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        # Evaluar alineación vertical (caderas por debajo de los hombros)
        cadera_izq_correcta = cadera_izq.y > hombro_izq.y + umbral
        cadera_der_correcta = cadera_der.y > hombro_der.y + umbral

        # Evaluar postura general
        movimiento_correcto = cadera_izq_correcta and cadera_der_correcta

        # Formatear resultados
        mensaje = (
            "Movimiento de preparación correcto" if movimiento_correcto
            else "Ajustar movimiento de preparación: las caderas deben estar por debajo de los hombros."
        )
        datos = {
            "cadera_izq_y": cadera_izq.y,
            "cadera_der_y": cadera_der.y,
            "hombro_izq_y": hombro_izq.y,
            "hombro_der_y": hombro_der.y,
            "cadera_izq_correcta": cadera_izq_correcta,
            "cadera_der_correcta": cadera_der_correcta
        }

        return {"mensaje": mensaje, "movimiento_correcto": movimiento_correcto, "datos": datos}

    except Exception as e:
        return {"mensaje": f"Error en la evaluación: {e}", "movimiento_correcto": False, "datos": {}}
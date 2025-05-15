import mediapipe as mp
from typing import List, Dict, Union

mp_pose = mp.solutions.pose

def validar_landmarks(landmarks: List, indices: List[int]) -> bool:
    """
    Valida que los landmarks sean una lista y contengan los índices necesarios.
    Args:
        landmarks (list): Lista de landmarks detectados.
        indices (list): Índices de landmarks requeridos.
    Returns:
        bool: True si los landmarks son válidos, False en caso contrario.
    """
    if not isinstance(landmarks, list) or not all(0 <= idx < len(landmarks) for idx in indices):
        return False
    return True

def evaluar_seguimiento(
    landmarks: List,
    lado: str = "izquierdo",
    criterio: str = "altura"
) -> Dict[str, Union[str, bool, Dict[str, float]]]:
    """
    Evalúa el seguimiento de un brazo basado en los landmarks proporcionados.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
        lado (str): Lado del cuerpo a evaluar ("izquierdo" o "derecho").
        criterio (str): Criterio de evaluación ("altura" para comparar posiciones verticales).
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Mapear los landmarks según el lado
        if lado == "izquierdo":
            codo_idx = mp_pose.PoseLandmark.LEFT_ELBOW.value
            hombro_idx = mp_pose.PoseLandmark.LEFT_SHOULDER.value
        elif lado == "derecho":
            codo_idx = mp_pose.PoseLandmark.RIGHT_ELBOW.value
            hombro_idx = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
        else:
            raise ValueError("El lado debe ser 'izquierdo' o 'derecho'.")

        # Validar landmarks
        if not validar_landmarks(landmarks, [codo_idx, hombro_idx]):
            raise ValueError("Landmarks inválidos o incompletos.")

        # Obtener los landmarks
        codo = landmarks[codo_idx]
        hombro = landmarks[hombro_idx]

        # Evaluar seguimiento según el criterio
        seguimiento_correcto = False
        if criterio == "altura":
            seguimiento_correcto = codo.y < hombro.y
        else:
            raise ValueError("Criterio no soportado. Use 'altura'.")

        # Formatear resultados
        mensaje = (
            f"Seguimiento {'correcto' if seguimiento_correcto else 'incorrecto'} "
            f"para el brazo {lado}."
        )
        datos = {
            "codo_y": codo.y,
            "hombro_y": hombro.y,
            "seguimiento_correcto": seguimiento_correcto,
        }

        return {"mensaje": mensaje, "datos": datos}

    except Exception as e:
        return {"mensaje": f"Error en la evaluación: {e}", "datos": {}}
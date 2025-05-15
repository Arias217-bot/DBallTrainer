import mediapipe as mp
from typing import Dict, Union

mp_pose = mp.solutions.pose

def validar_landmarks(landmarks: Dict, indices: list) -> bool:
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

def calcular_diferencia_landmarks(landmark1, landmark2) -> Dict[str, float]:
    """
    Calcula las diferencias en los ejes X e Y entre dos landmarks.
    Args:
        landmark1: Primer landmark con atributos x, y.
        landmark2: Segundo landmark con atributos x, y.
    Returns:
        dict: Diferencias en los ejes X e Y.
    """
    return {
        "diferencia_x": abs(landmark1.x - landmark2.x),
        "diferencia_y": abs(landmark1.y - landmark2.y)
    }

def evaluar_estabilidad(
    landmarks: Dict,
    umbral_y: float = 0.1,
    umbral_x: float = 0.2,
    debug: bool = False
) -> Dict[str, Union[str, bool, Dict[str, float]]]:
    """
    Evalúa la estabilidad del usuario basándose en la posición de los pies.
    Args:
        landmarks (dict): Diccionario de landmarks detectados por MediaPipe.
        umbral_y (float): Tolerancia para la diferencia en el eje Y (altura).
        umbral_x (float): Tolerancia para la diferencia en el eje X (separación lateral).
        debug (bool): Si es True, imprime información adicional para depuración.
    Returns:
        dict: Resultado de la evaluación con un mensaje descriptivo y datos relevantes.
    """
    try:
        # Validar landmarks
        indices_necesarios = [
            mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value,
            mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
        ]
        if not validar_landmarks(landmarks, indices_necesarios):
            raise ValueError("Landmarks inválidos o incompletos.")

        # Obtener los landmarks de los pies
        pie_derecho = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
        pie_izquierdo = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]

        # Calcular diferencias en los ejes X e Y
        diferencias = calcular_diferencia_landmarks(pie_derecho, pie_izquierdo)

        # Evaluar estabilidad
        estabilidad_correcta = (
            diferencias["diferencia_y"] < umbral_y and
            diferencias["diferencia_x"] < umbral_x
        )

        # Mensaje descriptivo
        if estabilidad_correcta:
            mensaje = "Estabilidad correcta"
        else:
            mensaje = (
                f"Ajustar estabilidad: diferencia Y={diferencias['diferencia_y']:.2f}, "
                f"diferencia X={diferencias['diferencia_x']:.2f}"
            )

        # Depuración opcional
        if debug:
            print(f"[DEBUG] Diferencias: {diferencias}")
            print(f"[DEBUG] Estabilidad correcta: {estabilidad_correcta}")

        # Retornar resultados
        return {
            "mensaje": mensaje,
            "estable": estabilidad_correcta,
            "datos": {
                "diferencia_y": diferencias["diferencia_y"],
                "diferencia_x": diferencias["diferencia_x"],
                "umbral_y": umbral_y,
                "umbral_x": umbral_x
            }
        }

    except Exception as e:
        if debug:
            print(f"[DEBUG] Error en evaluar_estabilidad: {e}")
        return {
            "mensaje": "Error al evaluar la estabilidad",
            "estable": False,
            "datos": {}
        }
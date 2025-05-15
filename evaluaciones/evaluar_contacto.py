import mediapipe as mp
import math
from mediapipe.python.solutions.pose import PoseLandmark

mp_pose = mp.solutions.pose

def calcular_angulo(p1, p2, p3):
    """
    Calcula el ángulo entre tres puntos.
    Args:
        p1, p2, p3: Puntos con atributos x, y.
    Returns:
        float: Ángulo en grados ajustado o None si ocurre un error.
    """
    try:
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        angulo = abs(angulo)
        if angulo > 180:
            angulo = 360 - angulo
        return angulo
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def evaluar_contacto(
    landmarks,
    angulo_min: float = 75.0,
    angulo_max: float = 110.0,
    distancia_max: float = 0.2,
    debug: bool = False
) -> dict:
    """
    Evalúa si el contacto con el balón es correcto.
    Args:
        landmarks: Lista o dict de landmarks detectados por MediaPipe.
        angulo_min (float): Ángulo mínimo para considerar el contacto válido.
        angulo_max (float): Ángulo máximo para considerar el contacto válido.
        distancia_max (float): Distancia máxima entre muñeca y codo.
        debug (bool): Si es True, imprime información adicional para depuración.
    Returns:
        dict: Resultado de la evaluación con un mensaje descriptivo y datos relevantes.
    """
    try:
        # Validar estructura de entrada
        if not hasattr(landmarks, '__getitem__'):
            raise ValueError("Landmarks no son indexables.")

        # Obtener landmarks necesarios
        muñeca = landmarks[PoseLandmark.LEFT_WRIST.value]
        codo = landmarks[PoseLandmark.LEFT_ELBOW.value]
        hombro = landmarks[PoseLandmark.LEFT_SHOULDER.value]

        # Validar que no sean None
        if any(p is None for p in [muñeca, codo, hombro]):
            raise ValueError("Uno o más landmarks están vacíos.")

        # Calcular ángulo entre muñeca, codo y hombro
        angulo_brazo = calcular_angulo(muñeca, codo, hombro)
        if angulo_brazo is None:
            raise ValueError("No se pudo calcular el ángulo del brazo.")

        # Calcular distancia entre muñeca y codo
        distancia_mc = math.sqrt((muñeca.x - codo.x) ** 2 + (muñeca.y - codo.y) ** 2)

        # Evaluar contacto válido
        contacto_valido = (
            angulo_min <= angulo_brazo <= angulo_max and
            distancia_mc <= distancia_max and
            muñeca.y < codo.y + 0.02 < hombro.y + 0.05  # Condición más tolerante
        )

        # Mensaje descriptivo
        if contacto_valido:
            mensaje = "Contacto válido con el balón"
        else:
            mensaje = (
                f"Contacto incorrecto: ángulo={angulo_brazo:.2f}, "
                f"distancia_mc={distancia_mc:.2f}, "
                f"posición muñeca={muñeca.y:.2f}, codo={codo.y:.2f}, hombro={hombro.y:.2f}"
            )

        # Depuración opcional
        if debug:
            print(f"[DEBUG] Ángulo del brazo: {angulo_brazo:.2f}")
            print(f"[DEBUG] Distancia muñeca-codo: {distancia_mc:.2f}")
            print(f"[DEBUG] muñeca.y: {muñeca.y:.2f}, codo.y: {codo.y:.2f}, hombro.y: {hombro.y:.2f}")
            print(f"[DEBUG] Contacto válido: {contacto_valido}")

        # Retornar resultados
        return {
            "mensaje": mensaje,
            "valido": contacto_valido,
            "datos": {
                "angulo_brazo": angulo_brazo,
                "distancia_mc": distancia_mc,
                "muñeca_y": muñeca.y,
                "codo_y": codo.y,
                "hombro_y": hombro.y
            }
        }

    except Exception as e:
        if debug:
            print(f"[DEBUG] Error en evaluar_contacto: {e}")
            print(f"[DEBUG] Landmarks recibidos: {landmarks}")
        return {
            "mensaje": f"Error al evaluar el contacto: {str(e)}",
            "valido": False,
            "datos": {}
        }

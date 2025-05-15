import math
from mediapipe.python.solutions.pose import PoseLandmark
from evaluaciones import evaluar_contacto

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def calcular_velocidad_angular(angulo_actual, angulo_anterior, tiempo):
    """Calcula la velocidad angular entre dos ángulos dados un intervalo de tiempo."""
    try:
        if tiempo <= 0:
            return 0
        return abs(angulo_actual - angulo_anterior) / tiempo
    except Exception as e:
        print(f"Error al calcular la velocidad angular: {e}")
        return None

def detectar_ataque(landmarks, angulos_anteriores=None, tiempo=1, tolerancia_simetria=15):
    """
    Detecta y evalúa la técnica de ataque en voleibol.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
        angulos_anteriores (dict): Diccionario con los ángulos previos de los codos.
        tiempo (float): Intervalo de tiempo entre frames.
        tolerancia_simetria (int): Tolerancia en grados para evaluar la simetría entre brazos.
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar landmarks
        required_landmarks = [
            PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_ELBOW.value, PoseLandmark.LEFT_WRIST.value,
            PoseLandmark.RIGHT_SHOULDER.value, PoseLandmark.RIGHT_ELBOW.value, PoseLandmark.RIGHT_WRIST.value
        ]
        if not isinstance(landmarks, list) or not all(idx < len(landmarks) for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para evaluar el ataque.")

        # Extraer landmarks relevantes
        hombro_izq = landmarks[PoseLandmark.LEFT_SHOULDER.value]
        codo_izq = landmarks[PoseLandmark.LEFT_ELBOW.value]
        muñeca_izq = landmarks[PoseLandmark.LEFT_WRIST.value]

        hombro_der = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo_der = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca_der = landmarks[PoseLandmark.RIGHT_WRIST.value]

        # Calcular ángulos de los codos
        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_codo_der = calcular_angulo(hombro_der, codo_der, muñeca_der)

        # Validar que los ángulos sean válidos
        if None in [angulo_codo_izq, angulo_codo_der]:
            raise ValueError("No se pudieron calcular algunos ángulos.")

        # Calcular velocidad angular de los codos
        velocidad_angular_izq = calcular_velocidad_angular(
            angulo_codo_izq, angulos_anteriores.get("angulo_codo_izq", angulo_codo_izq), tiempo
        ) if angulos_anteriores else 0
        velocidad_angular_der = calcular_velocidad_angular(
            angulo_codo_der, angulos_anteriores.get("angulo_codo_der", angulo_codo_der), tiempo
        ) if angulos_anteriores else 0

        # Evaluar si el ataque es válido
        ataque_valido_izq = angulo_codo_izq > 90
        ataque_valido_der = angulo_codo_der > 90
        ataque_valido = ataque_valido_izq or ataque_valido_der

        # Evaluar contacto con el balón
        contacto_valido = evaluar_contacto(landmarks)

        # Calcular simetría entre los brazos
        simetria = abs(angulo_codo_izq - angulo_codo_der) < tolerancia_simetria  # Tolerancia ajustable

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo izquierdo: {angulo_codo_izq:.2f}° ({'válido' if ataque_valido_izq else 'no válido'})",
            f"Ángulo del codo derecho: {angulo_codo_der:.2f}° ({'válido' if ataque_valido_der else 'no válido'})",
            f"Velocidad angular codo izquierdo: {velocidad_angular_izq:.2f}°/s",
            f"Velocidad angular codo derecho: {velocidad_angular_der:.2f}°/s",
            f"Ataque {'válido' if ataque_valido else 'no válido'}",
            f"Contacto con el balón: {'correcto' if contacto_valido else 'incorrecto'}",
            f"Simetría entre brazos: {'Correcta' if simetria else 'Incorrecta'}"
        ]

        # Salida estructurada
        return {
            "mensajes": mensajes,
            "datos": [
                angulo_codo_izq, angulo_codo_der, velocidad_angular_izq, velocidad_angular_der,
                ataque_valido, contacto_valido, simetria
            ]
        }

    except Exception as e:
        print(f"Error en detectar_ataque: {e}")
        return {
            "mensajes": ["Error en la detección del ataque"],
            "datos": [None, None, None, None, None, None, None]
        }

def obtener_encabezados_ataque():
    """Devuelve los encabezados específicos para la detección de ataque."""
    return [
        "Angulo Codo Izq", "Angulo Codo Der", "Velocidad Angular Codo Izq", "Velocidad Angular Codo Der",
        "Ataque Valido", "Contacto Valido", "Simetria"
    ]
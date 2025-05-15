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

def detectar_saque(landmarks):
    """
    Detecta un saque basado en los landmarks proporcionados.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar que landmarks sea una lista y contenga los landmarks necesarios
        required_landmarks = [
            PoseLandmark.RIGHT_SHOULDER.value,
            PoseLandmark.RIGHT_ELBOW.value,
            PoseLandmark.RIGHT_WRIST.value
        ]
        if not isinstance(landmarks, list) or not all(idx < len(landmarks) for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para evaluar el saque.")

        # Acceder a landmarks individuales
        hombro = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca = landmarks[PoseLandmark.RIGHT_WRIST.value]

        # Validar altura inicial del brazo: la muñeca debe estar por encima del hombro
        altura_brazo_correcta = muñeca.y < hombro.y

        # Calcular ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")

        # Evaluar alineación: hombro, codo y muñeca deben estar alineados en x (umbral de 0.1)
        alineacion_hombro = abs(hombro.x - codo.x) < 0.1
        alineacion_codo = abs(codo.x - muñeca.x) < 0.1

        # Evaluar contacto con el balón
        contacto_valido = evaluar_contacto(landmarks)

        # Evaluar si el saque es válido: se esperan condiciones correctas en todos los parámetros
        saque_valido = angulo_codo > 90 and altura_brazo_correcta and alineacion_hombro and alineacion_codo and contacto_valido

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo: {angulo_codo:.2f}°",
            f"Altura del brazo: {'Correcta' if altura_brazo_correcta else 'Incorrecta'}",
            f"Alineación del hombro: {'Correcta' if alineacion_hombro else 'Incorrecta'}",
            f"Alineación del codo: {'Correcta' if alineacion_codo else 'Incorrecta'}",
            f"Contacto con el balón: {'Correcto' if contacto_valido else 'Incorrecto'}",
            f"Saque {'válido' if saque_valido else 'no válido'}"
        ]

        # Salida estructurada
        return {
            "mensajes": mensajes,
            "datos": [
                angulo_codo, altura_brazo_correcta, alineacion_hombro, 
                alineacion_codo, contacto_valido, saque_valido
            ]
        }

    except Exception as e:
        print(f"Error en detectar_saque: {e}")
        return {
            "mensajes": ["Error en la detección del saque"],
            "datos": [None, None, None, None, None, False]
        }

def obtener_encabezados_saque():
    """Devuelve los encabezados específicos para la detección de saque."""
    return [
        "Angulo Codo", "Altura Brazo", "Alineacion Hombro", 
        "Alineacion Codo", "Contacto Balon", "Saque Valido"
    ]
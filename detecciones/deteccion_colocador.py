import math
from mediapipe.python.solutions.pose import PoseLandmark
from evaluaciones import evaluar_movimiento

def calcular_angulo(a, b, c):
    """Calcula el ángulo entre tres puntos."""
    try:
        a = [a.x, a.y]
        b = [b.x, b.y]
        c = [c.x, c.y]
        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]
        coseno_angulo = (ba[0] * bc[0] + ba[1] * bc[1]) / (math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2))
        angulo = math.acos(max(min(coseno_angulo, 1), -1))
        return math.degrees(angulo)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def detectar_colocador(landmarks):
    """
    Detecta la postura del colocador basado en los puntos de referencia del cuerpo.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar landmarks
        required_landmarks = [
            PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_ELBOW.value, PoseLandmark.LEFT_WRIST.value,
            PoseLandmark.RIGHT_SHOULDER.value, PoseLandmark.RIGHT_ELBOW.value, PoseLandmark.RIGHT_WRIST.value,
            PoseLandmark.LEFT_HIP.value, PoseLandmark.LEFT_KNEE.value, PoseLandmark.LEFT_ANKLE.value,
            PoseLandmark.RIGHT_HIP.value, PoseLandmark.RIGHT_KNEE.value, PoseLandmark.RIGHT_ANKLE.value,
            PoseLandmark.LEFT_EYE.value, PoseLandmark.RIGHT_EYE.value
        ]
        if not isinstance(landmarks, list) or not all(idx < len(landmarks) for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para evaluar al colocador.")

        # Acceder a landmarks individuales
        hombro_izq, codo_izq, muñeca_izq = (
            landmarks[PoseLandmark.LEFT_SHOULDER.value],
            landmarks[PoseLandmark.LEFT_ELBOW.value],
            landmarks[PoseLandmark.LEFT_WRIST.value]
        )
        hombro_der, codo_der, muñeca_der = (
            landmarks[PoseLandmark.RIGHT_SHOULDER.value],
            landmarks[PoseLandmark.RIGHT_ELBOW.value],
            landmarks[PoseLandmark.RIGHT_WRIST.value]
        )
        cadera_izq, rodilla_izq, tobillo_izq = (
            landmarks[PoseLandmark.LEFT_HIP.value],
            landmarks[PoseLandmark.LEFT_KNEE.value],
            landmarks[PoseLandmark.LEFT_ANKLE.value]
        )
        cadera_der, rodilla_der, tobillo_der = (
            landmarks[PoseLandmark.RIGHT_HIP.value],
            landmarks[PoseLandmark.RIGHT_KNEE.value],
            landmarks[PoseLandmark.RIGHT_ANKLE.value]
        )
        ceja_izq = landmarks[PoseLandmark.LEFT_EYE.value]
        ceja_der = landmarks[PoseLandmark.RIGHT_EYE.value]

        # Calcular ángulos
        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_rodilla_izq = calcular_angulo(cadera_izq, rodilla_izq, tobillo_izq)
        angulo_tronco_izq = calcular_angulo(hombro_izq, cadera_izq, rodilla_izq)

        angulo_codo_der = calcular_angulo(hombro_der, codo_der, muñeca_der)
        angulo_rodilla_der = calcular_angulo(cadera_der, rodilla_der, tobillo_der)
        angulo_tronco_der = calcular_angulo(hombro_der, cadera_der, rodilla_der)

        # Verificar si los ángulos son válidos
        if None in [angulo_codo_izq, angulo_rodilla_izq, angulo_tronco_izq,
                    angulo_codo_der, angulo_rodilla_der, angulo_tronco_der]:
            return {"mensajes": ["No se pudieron calcular algunos ángulos"], "datos": [None] * 9}

        # Evaluar si las manos están sobre la frente
        manos_sobre_frente_izq = muñeca_izq.y < ceja_izq.y
        manos_sobre_frente_der = muñeca_der.y < ceja_der.y

        # Evaluar movimiento controlado
        movimiento_controlado = not evaluar_movimiento(landmarks)

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo codo izquierdo: {angulo_codo_izq:.2f}°",
            f"Ángulo codo derecho: {angulo_codo_der:.2f}°",
            f"Mano izquierda sobre la frente: {'Sí' if manos_sobre_frente_izq else 'No'}",
            f"Mano derecha sobre la frente: {'Sí' if manos_sobre_frente_der else 'No'}",
            f"Movimiento: {'Controlado' if movimiento_controlado else 'Excesivo'}"
        ]

        # Salida estructurada
        return {
            "mensajes": mensajes,
            "datos": [
                angulo_codo_izq, angulo_rodilla_izq, angulo_tronco_izq, manos_sobre_frente_izq,
                angulo_codo_der, angulo_rodilla_der, angulo_tronco_der, manos_sobre_frente_der,
                movimiento_controlado
            ]
        }

    except Exception as e:
        print(f"Error en detectar_colocador: {e}")
        return {
            "mensajes": ["Error en la detección del colocador"],
            "datos": [None] * 9
        }

def obtener_encabezados_colocador():
    """Devuelve los encabezados específicos para la detección del colocador."""
    return [
        "Angulo Codo Izq", "Angulo Rodilla Izq", "Angulo Tronco Izq", "Mano Izq Sobre Frente",
        "Angulo Codo Der", "Angulo Rodilla Der", "Angulo Tronco Der", "Mano Der Sobre Frente",
        "Movimiento Controlado"
    ]
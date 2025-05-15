import math
from mediapipe.python.solutions.pose import PoseLandmark
from evaluaciones import evaluar_contacto, evaluar_posicion, evaluar_movimiento, evaluar_sentadillas

def calcular_angulo(a, b, c):
    """Calcula el ángulo entre tres puntos en coordenadas de píxeles."""
    try:
        a, b, c = (a.x, a.y), (b.x, b.y), (c.x, c.y)
        ba = (a[0] - b[0], a[1] - b[1])
        bc = (c[0] - b[0], c[1] - b[1])
        cos_angulo = (ba[0] * bc[0] + ba[1] * bc[1]) / (math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2))
        angulo = math.acos(max(min(cos_angulo, 1), -1))
        return math.degrees(angulo)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def detectar_postura(landmarks):
    """
    Detecta y evalúa la postura basada en los puntos de referencia del cuerpo.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
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
            raise ValueError("Faltan landmarks esenciales para evaluar la postura.")

        # Obtener puntos clave para ambos lados
        puntos_clave = {
            "izquierdo": {
                "hombro": landmarks[PoseLandmark.LEFT_SHOULDER.value],
                "codo": landmarks[PoseLandmark.LEFT_ELBOW.value],
                "muñeca": landmarks[PoseLandmark.LEFT_WRIST.value]
            },
            "derecho": {
                "hombro": landmarks[PoseLandmark.RIGHT_SHOULDER.value],
                "codo": landmarks[PoseLandmark.RIGHT_ELBOW.value],
                "muñeca": landmarks[PoseLandmark.RIGHT_WRIST.value]
            }
        }

        # Evaluaciones para ambos lados
        evaluaciones = {}
        for lado, puntos in puntos_clave.items():
            angulo_codo = calcular_angulo(puntos["hombro"], puntos["codo"], puntos["muñeca"])
            posicion_correcta = evaluar_posicion(landmarks)
            contacto_brazos = evaluar_contacto([landmarks[PoseLandmark.LEFT_WRIST.value],
                                                landmarks[PoseLandmark.RIGHT_WRIST.value]])
            sentadilla_correcta = evaluar_sentadillas(landmarks)
            movimiento_excesivo = evaluar_movimiento(landmarks)

            evaluaciones[lado] = {
                "angulo_codo": angulo_codo,
                "posicion_correcta": posicion_correcta,
                "contacto_brazos": contacto_brazos,
                "sentadilla_correcta": sentadilla_correcta,
                "movimiento_excesivo": movimiento_excesivo
            }

        # Mensajes descriptivos
        mensajes = []
        datos = []
        for lado, evals in evaluaciones.items():
            mensajes.append(f"{lado.capitalize()} - Ángulo del codo: {evals['angulo_codo']:.2f}°")
            mensajes.append(f"{lado.capitalize()} - Posición corporal: {'Correcta' if evals['posicion_correcta'] else 'Incorrecta'}")
            mensajes.append(f"{lado.capitalize()} - Contacto con el balón: {'Correcto' if evals['contacto_brazos'] else 'Incorrecto'}")
            mensajes.append(f"{lado.capitalize()} - Sentadilla: {'Correcta' if evals['sentadilla_correcta'] else 'Incorrecta'}")
            mensajes.append(f"{lado.capitalize()} - Movimiento: {'Controlado' if not evals['movimiento_excesivo'] else 'Excesivo'}")

            # Datos para el CSV
            datos.extend([
                evals["angulo_codo"],
                evals["posicion_correcta"],
                evals["contacto_brazos"],
                evals["sentadilla_correcta"],
                not evals["movimiento_excesivo"]
            ])

        # Salida estructurada
        return {
            "mensajes": mensajes,
            "datos": datos
        }

    except Exception as e:
        print(f"Error en detectar_postura: {e}")
        return {
            "mensajes": ["Error en la detección de la postura"],
            "datos": [None] * 10  # 5 datos por lado (izquierdo y derecho)
        }
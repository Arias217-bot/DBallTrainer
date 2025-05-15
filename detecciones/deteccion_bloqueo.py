import math
from mediapipe.python.solutions.pose import PoseLandmark

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

def calcular_distancia(p1, p2):
    """Calcula la distancia euclidiana entre dos puntos."""
    try:
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
    except Exception as e:
        print(f"Error al calcular la distancia: {e}")
        return None

def detectar_bloqueo(landmarks, tolerancia_simetria=15):
    """
    Detecta y evalúa la técnica de bloqueo en voleibol.
    
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
        tolerancia_simetria (int): Tolerancia en grados para evaluar la simetría entre brazos.
        
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
              Los datos retornados deben tener 8 columnas para que, junto con el "Frame",
              se obtengan 9 columnas en el CSV:
              [Angulo Brazo Izq, Angulo Brazo Der, Altura Bloqueo Izq, Altura Bloqueo Der, 
               Alineación Tronco, Bloqueo Válido, Separación de Manos, Simetría]
    """
    try:
        # Validar landmarks necesarios
        required_landmarks = [
            PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_ELBOW.value, PoseLandmark.LEFT_WRIST.value,
            PoseLandmark.RIGHT_SHOULDER.value, PoseLandmark.RIGHT_ELBOW.value, PoseLandmark.RIGHT_WRIST.value,
            PoseLandmark.NOSE.value, PoseLandmark.LEFT_HIP.value, PoseLandmark.RIGHT_HIP.value
        ]
        if not isinstance(landmarks, list) or not all(idx < len(landmarks) for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para evaluar el bloqueo.")

        # Extraer landmarks relevantes
        hombro_izq = landmarks[PoseLandmark.LEFT_SHOULDER.value]
        codo_izq = landmarks[PoseLandmark.LEFT_ELBOW.value]
        muñeca_izq = landmarks[PoseLandmark.LEFT_WRIST.value]

        hombro_der = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo_der = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca_der = landmarks[PoseLandmark.RIGHT_WRIST.value]

        cabeza = landmarks[PoseLandmark.NOSE.value]
        cadera_izq = landmarks[PoseLandmark.LEFT_HIP.value]
        cadera_der = landmarks[PoseLandmark.RIGHT_HIP.value]

        # Calcular ángulos de los brazos
        angulo_brazos_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_brazos_der = calcular_angulo(hombro_der, codo_der, muñeca_der)

        # Altura del bloqueo (normalizada usando la cabeza como referencia)
        altura_bloqueo_izq = muñeca_izq.y / cabeza.y
        altura_bloqueo_der = muñeca_der.y / cabeza.y

        # Calcular alineación del tronco (entre hombros y caderas)
        angulo_tronco = calcular_angulo(cadera_izq, hombro_izq, hombro_der)

        # Calcular separación de manos
        separacion_manos = calcular_distancia(muñeca_izq, muñeca_der)

        # Verificar que se calcularon todos los valores
        if None in [angulo_brazos_izq, angulo_brazos_der, altura_bloqueo_izq,
                    altura_bloqueo_der, angulo_tronco, separacion_manos]:
            return {"mensajes": ["No se pudieron calcular algunos valores."],
                    "datos": [None] * 8}

        # Criterios de bloqueo válido
        bloqueo_valido_izq = angulo_brazos_izq > 160 and altura_bloqueo_izq < 0.5
        bloqueo_valido_der = angulo_brazos_der > 160 and altura_bloqueo_der < 0.5
        tronco_alineado = 75 <= angulo_tronco <= 105      
        bloqueo_valido = bloqueo_valido_izq and bloqueo_valido_der and tronco_alineado

        # Calcular simetría entre los brazos
        simetria = abs(angulo_brazos_izq - angulo_brazos_der) < tolerancia_simetria

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo brazo izquierdo: {angulo_brazos_izq:.2f}° ({'Correcto' if bloqueo_valido_izq else 'Incorrecto'})",
            f"Ángulo brazo derecho: {angulo_brazos_der:.2f}° ({'Correcto' if bloqueo_valido_der else 'Incorrecto'})",
            f"Altura muñeca izquierda: {'Correcta' if altura_bloqueo_izq < 0.5 else 'Demasiado baja'}",
            f"Altura muñeca derecha: {'Correcta' if altura_bloqueo_der < 0.5 else 'Demasiado baja'}",
            f"Tronco {'Alineado' if tronco_alineado else 'Desalineado'}",
            f"Bloqueo {'Válido' if bloqueo_valido else 'No válido'}",
            f"Separación de manos: {separacion_manos:.2f}",
            f"Simetría entre brazos: {'Correcta' if simetria else 'Incorrecta'}"
        ]

        # Retornar los datos en el orden esperado:
        # [Angulo Brazo Izq, Angulo Brazo Der, Altura Bloqueo Izq, Altura Bloqueo Der,
        #  Alineación Tronco, Bloqueo Válido, Separación de Manos, Simetría]
        return {
            "mensajes": mensajes,
            "datos": [
                angulo_brazos_izq,
                angulo_brazos_der,
                altura_bloqueo_izq,
                altura_bloqueo_der,
                angulo_tronco,
                bloqueo_valido,
                separacion_manos,
                simetria
            ]
        }

    except Exception as e:
        print(f"Error en detectar_bloqueo: {e}")
        return {
            "mensajes": ["Error en la detección de bloqueo"],
            "datos": [None] * 8
        }

def obtener_encabezados_bloqueo():
    """Devuelve los encabezados específicos para la detección de bloqueo."""
    return [
        "Angulo Brazo Izq", "Angulo Brazo Der", "Altura Bloqueo Izq", "Altura Bloqueo Der",
        "Alineación Tronco", "Bloqueo Válido", "Separación de Manos", "Simetría"
    ]
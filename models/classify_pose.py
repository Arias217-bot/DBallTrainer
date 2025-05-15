import numpy as np
import logging
from detecciones import (
    detectar_saque,
    detectar_colocador,
    detectar_ataque,
    detectar_recibo,
    detectar_bloqueo
)

# Configuración básica del logger para poder emitir warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClassifyPose:
    """
    Clase para clasificar las acciones de múltiples personas a partir de sus keypoints.
    Detecta posiciones específicas del voleibol como saque, ataque, bloqueo, etc.
    """

    def __init__(self):
        """
        Inicializa la clase ClassifyPose.
        """
        pass

    def classify(self, keypoints_list):
        """
        Clasifica las acciones de múltiples personas a partir de sus keypoints.

        Parámetros:
            keypoints_list (list): Lista de arreglos de keypoints, uno por cada persona.

        Retorna:
            dict: Diccionario con las acciones detectadas para cada persona.
        """
        resultados = {}

        try:
            # Validar que la entrada sea una lista y que cada elemento sea un arreglo (lista o np.ndarray)
            if not isinstance(keypoints_list, list) or not all(isinstance(kp, (list, np.ndarray)) for kp in keypoints_list):
                raise ValueError("La entrada debe ser una lista de listas o numpy arrays con keypoints.")

            for idx, keypoints_array in enumerate(keypoints_list):
                # Validar que cada arreglo tenga formato correcto (múltiplo de 3)
                if len(keypoints_array) % 3 != 0:
                    resultados[f"persona_{idx}"] = "Error: Keypoints no válidos"
                    continue

                # Se llama a cada función de detección y se evalúa un criterio
                # Nota: Se asume que cada función retorna un dict con la clave "datos"
                # que contiene una lista con una cantidad exacta de elementos según su detección.

                # Detección de Saque: Se esperan 7 elementos (índice 6 para valida saque)
                res_saque = detectar_saque(keypoints_array)
                if res_saque and "datos" in res_saque:
                    if len(res_saque["datos"]) != 7:
                        logger.warning(f"Cantidad de datos inesperada para detección de Saque en persona_{idx}: {len(res_saque['datos'])} elementos.")
                    else:
                        if res_saque["datos"][6]:
                            resultados[f"persona_{idx}"] = "Saque"
                            continue

                # Detección de Ataque: Se esperan 9 elementos (índice 4 indica ataque válido)
                res_ataque = detectar_ataque(keypoints_array)
                if res_ataque and "datos" in res_ataque:
                    if len(res_ataque["datos"]) != 9:
                        logger.warning(f"Cantidad de datos inesperada para detección de Ataque en persona_{idx}: {len(res_ataque['datos'])} elementos.")
                    else:
                        if res_ataque["datos"][4]:
                            resultados[f"persona_{idx}"] = "Ataque"
                            continue

                # Detección de Bloqueo: Se esperan 9 elementos (índice 5 indica bloqueo válido)
                res_bloqueo = detectar_bloqueo(keypoints_array)
                if res_bloqueo and "datos" in res_bloqueo:
                    if len(res_bloqueo["datos"]) != 9:
                        logger.warning(f"Cantidad de datos inesperada para detección de Bloqueo en persona_{idx}: {len(res_bloqueo['datos'])} elementos.")
                    else:
                        if res_bloqueo["datos"][5]:
                            resultados[f"persona_{idx}"] = "Bloqueo"
                            continue

                # Detección de Recibo: Se esperan 7 elementos (índice 2 indica posición correcta)
                res_recibo = detectar_recibo(keypoints_array)
                if res_recibo and "datos" in res_recibo:
                    if len(res_recibo["datos"]) != 7:
                        logger.warning(f"Cantidad de datos inesperada para detección de Recibo en persona_{idx}: {len(res_recibo['datos'])} elementos.")
                    else:
                        if res_recibo["datos"][2]:
                            resultados[f"persona_{idx}"] = "Recibo"
                            continue

                # Detección de Colocador: Se esperan 10 elementos
                res_colocador = detectar_colocador(keypoints_array)
                if res_colocador and "datos" in res_colocador:
                    if len(res_colocador["datos"]) != 10:
                        logger.warning(f"Cantidad de datos inesperada para detección de Colocador en persona_{idx}: {len(res_colocador['datos'])} elementos.")
                    else:
                        # Si la detección es exitosa, se asigna "Colocador"
                        resultados[f"persona_{idx}"] = "Colocador"
                        continue

                resultados[f"persona_{idx}"] = "Indeterminado"

        except Exception as e:
            logger.error(f"Error en classify_pose: {e}")
            return {"error": "Error general en la clasificación"}

        return resultados

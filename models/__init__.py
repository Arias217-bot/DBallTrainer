# Importar todas las clases y funciones relevantes del módulo
from .classify_pose import ClassifyPose

# Definir explícitamente qué se exporta cuando se importa el paquete
__all__ = [
    ClassifyPose,  # Clase para clasificar poses
]

# Agregar un comentario para describir el propósito del módulo
"""
Este paquete contiene modelos y herramientas para la clasificación de poses
y otras funcionalidades relacionadas con el análisis de movimientos.
"""
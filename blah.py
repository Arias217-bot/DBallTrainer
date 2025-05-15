from detecciones import (
    obtener_encabezados_ataque,
    obtener_encabezados_bloqueo,
    obtener_encabezados_colocador,
    obtener_encabezados_recibo,
    obtener_encabezados_saque,
)

def imprimir_todos_los_encabezados():
    """
    Llama a todas las funciones de encabezados y los imprime con su origen.
    """
    # Diccionario de funciones para cada tipo de análisis
    funciones_encabezados = {
        "ataque": obtener_encabezados_ataque,
        "bloqueo": obtener_encabezados_bloqueo,
        "colocador": obtener_encabezados_colocador,
        "saque": obtener_encabezados_saque,
        "recibo": obtener_encabezados_recibo,
    }

    # Recorrer todas las funciones y obtener los encabezados
    print("Encabezados por tipo de análisis:")
    for tipo_analisis, funcion_encabezados in funciones_encabezados.items():
        encabezados = funcion_encabezados()  # Llamar a la función correspondiente
        print(f"[{tipo_analisis}]: {encabezados}")

# Llamar a la función para imprimir todos los encabezados
imprimir_todos_los_encabezados()
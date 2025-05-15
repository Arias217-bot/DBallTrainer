# -----------------------------
# LIBRERÍAS NECESARIAS
# -----------------------------
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from tkinter import Tk, filedialog
import os
import json

# -----------------------------
# FUNCIONES
# -----------------------------
def seleccionar_archivo() -> Path:
    """Permite seleccionar un archivo JSON usando un cuadro de diálogo."""
    print("Seleccione el archivo JSON para el análisis:")
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    return Path(file_path) if file_path else None

def cargar_datos_json(file_path):
    """Carga los datos desde un archivo JSON, normaliza nombres de columnas y elimina filas vacías."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            datos = json.load(f)
        df = pd.DataFrame(datos)
        # Normalizar nombres de columnas: quitar espacios, reemplazar por puntos
        df.columns = df.columns.str.strip().str.replace(" ", ".", regex=False)
        print("Nombres de columnas después de cargar y normalizar:", df.columns)
        # Eliminar filas donde todos los valores, excepto 'Frame', sean nulos
        if "Frame" in df.columns:
            df = df.dropna(how="all", subset=[col for col in df.columns if col != "Frame"])
        else:
            df = df.dropna(how="all")  # Si no hay 'Frame', eliminar filas completamente vacías
        return df
    except Exception as e:
        raise RuntimeError(f"Error al cargar archivo JSON: {e}")

# -----------------------------
# CLASE PRINCIPAL
# -----------------------------
class AnalisisEstadistico:
    """
    Clase para realizar análisis estadísticos y generar recomendaciones
    basadas en los datos de detección.
    """

    def __init__(self, json_path: str, tipo_analisis: str):
        self.json_path = json_path
        self.tipo_analisis = tipo_analisis.lower()
        self.data = None
        self.carpeta_resultados = Path(f"Estadistica/Resultados/{self.tipo_analisis.capitalize()}")

    def cargar_datos(self):
        """Carga los datos desde el archivo JSON y los asigna a self.data."""
        try:
            self.data = cargar_datos_json(self.json_path)
            if self.data.empty:
                raise ValueError("El archivo JSON no contiene datos útiles.")
            print(f"Datos cargados correctamente desde: {self.json_path}")
        except Exception as e:
            raise RuntimeError(f"Error al cargar los datos: {e}")

    def crear_carpeta_resultados(self):
        """Crea una carpeta para guardar los resultados del análisis."""
        self.carpeta_resultados.mkdir(parents=True, exist_ok=True)
        print(f"Carpeta de resultados creada: {self.carpeta_resultados}")

    def guardar_recomendaciones(self, recomendaciones, resumen_path):
        """Guarda las recomendaciones en un archivo de texto."""
        if not isinstance(recomendaciones, list):
            raise ValueError("Las recomendaciones deben ser una lista.")

        if resumen_path.exists():
            print(f"Advertencia: El archivo {resumen_path} ya existe y será sobrescrito.")
        with open(resumen_path, "w", encoding="utf-8") as f:
            f.write("\n".join(recomendaciones))
        print(f"Recomendaciones guardadas en: {resumen_path}")

    def generar_recomendaciones_ataque(self):
        """Genera recomendaciones específicas para el análisis de ataque."""
        recomendaciones = []
        columnas_necesarias = [
            "Angulo.Codo.Izq", "Angulo.Codo.Der",
            "Velocidad.Angular.Codo.Izq", "Velocidad.Angular.Codo.Der",
            "Ataque.Valido", "Contacto.Valido", "Simetria"
        ]

        # Verificar columnas necesarias
        faltantes = [col for col in columnas_necesarias if col not in self.data.columns]
        if faltantes:
            recomendaciones.append(f"- Faltan las siguientes columnas: {', '.join(faltantes)}")
            return recomendaciones

        # Simetría de ángulos de codo
        umbral_diferencia_codo = 15  # Grados
        diferencia_media_codo = abs(self.data["Angulo.Codo.Izq"] - self.data["Angulo.Codo.Der"]).mean()
        evaluacion_codo = "buena" if diferencia_media_codo <= umbral_diferencia_codo else "a mejorar"
        recomendaciones.append(f"- Diferencia media entre codos: {diferencia_media_codo:.2f}° (Recomendado: <= {umbral_diferencia_codo}° - {evaluacion_codo}).")

        # Simetría de velocidad angular
        umbral_diferencia_velocidad = 1.0  # rad/s (ejemplo)
        diferencia_velocidad = abs(self.data["Velocidad.Angular.Codo.Izq"] - self.data["Velocidad.Angular.Codo.Der"]).mean()
        evaluacion_velocidad = "buena" if diferencia_velocidad <= umbral_diferencia_velocidad else "a mejorar"
        recomendaciones.append(f"- Diferencia media en velocidad angular de codos: {diferencia_velocidad:.2f} rad/s (Recomendado: <= {umbral_diferencia_velocidad:.1f} rad/s - {evaluacion_velocidad}).")

        # Porcentaje de ataques válidos
        umbral_ataques_validos = 0.85  # 85%
        porcentaje_ataques_validos = (self.data["Ataque.Valido"].sum() / len(self.data)) * 100
        evaluacion_validez_ataque = "alto" if porcentaje_ataques_validos >= umbral_ataques_validos * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de ataques válidos: {porcentaje_ataques_validos:.2f}% (Objetivo: >= {umbral_ataques_validos * 100:.0f}% - {evaluacion_validez_ataque}).")

        # Porcentaje de contactos válidos
        umbral_contactos_validos = 0.90  # 90%
        porcentaje_contactos_validos = (self.data["Contacto.Valido"].sum() / len(self.data)) * 100
        evaluacion_validez_contacto = "alto" if porcentaje_contactos_validos >= umbral_contactos_validos * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de contactos válidos: {porcentaje_contactos_validos:.2f}% (Objetivo: >= {umbral_contactos_validos * 100:.0f}% - {evaluacion_validez_contacto}).")

        # Simetría general
        umbral_simetria = 0.8  # Cercano a 1
        simetria_promedio = self.data["Simetria"].mean()
        evaluacion_simetria = "adecuada" if simetria_promedio >= umbral_simetria else "a mejorar"
        recomendaciones.append(f"- Nivel promedio de simetría: {simetria_promedio:.2f} (Ideal: cercano a 1 - {evaluacion_simetria}).")

        return recomendaciones

    def generar_recomendaciones_bloqueo(self):
        """Genera recomendaciones específicas para el análisis de bloqueo."""
        recomendaciones = []
        columnas_necesarias = [
            "Angulo.Brazo.Izq", "Angulo.Brazo.Der",
            "Altura.Bloqueo.Izq", "Altura.Bloqueo.Der",
            "Alineacion.Tronco", "Bloqueo.Valido",
            "Separacion.De.Manos", "Simetria"
        ]

        # Verificar columnas necesarias
        faltantes = [col for col in columnas_necesarias if col not in self.data.columns]
        if faltantes:
            recomendaciones.append(f"- Faltan las siguientes columnas: {', '.join(faltantes)}")
            return recomendaciones

        # Simetría de ángulos de brazos
        umbral_diferencia_brazos = 15  # Grados
        diferencia_media_brazos = abs(self.data["Angulo.Brazo.Izq"] - self.data["Angulo.Brazo.Der"]).mean()
        evaluacion_brazos = "buena" if diferencia_media_brazos <= umbral_diferencia_brazos else "a mejorar"
        recomendaciones.append(f"- Diferencia media entre brazos: {diferencia_media_brazos:.2f}° (Recomendado: <= {umbral_diferencia_brazos}° - {evaluacion_brazos}).")

        # Simetría de altura de bloqueo
        umbral_diferencia_altura = 5  # cm
        diferencia_media_altura = abs(self.data["Altura.Bloqueo.Izq"] - self.data["Altura.Bloqueo.Der"]).mean()
        evaluacion_altura = "buena" if diferencia_media_altura <= umbral_diferencia_altura else "a mejorar"
        recomendaciones.append(f"- Diferencia media de altura de bloqueo: {diferencia_media_altura:.2f} cm (Recomendado: <= {umbral_diferencia_altura} cm - {evaluacion_altura}).")

        # Alineación de tronco (promedio)
        umbral_alineacion_tronco = 5  # Grados de desviación (ejemplo)
        alineacion_tronco_promedio = abs(self.data["Alineacion.Tronco"].mean()) # Asumiendo que 0 es ideal
        evaluacion_tronco = "buena" if alineacion_tronco_promedio <= umbral_alineacion_tronco else "a mejorar"
        recomendaciones.append(f"- Nivel promedio de alineación del tronco: {alineacion_tronco_promedio:.2f} (Ideal: cercano a 0 - {evaluacion_tronco}).")

        # Separación de manos (promedio)
        rango_separacion_manos = (15, 25)  # cm (ejemplo)
        separacion_manos_promedio = self.data["Separacion.De.Manos"].mean()
        evaluacion_separacion = "adecuada" if rango_separacion_manos[0] <= separacion_manos_promedio <= rango_separacion_manos[1] else "a revisar"
        recomendaciones.append(f"- Promedio de separación de manos: {separacion_manos_promedio:.2f} cm (Rango típico: {rango_separacion_manos[0]}-{rango_separacion_manos[1]} cm - {evaluacion_separacion}).")

        # Porcentaje de bloqueos válidos
        umbral_bloqueos_validos = 0.75  # 75%
        porcentaje_bloqueos_validos = (self.data["Bloqueo.Valido"].sum() / len(self.data)) * 100
        evaluacion_validez_bloqueo = "alto" if porcentaje_bloqueos_validos >= umbral_bloqueos_validos * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de bloqueos válidos: {porcentaje_bloqueos_validos:.2f}% (Objetivo: >= {umbral_bloqueos_validos * 100:.0f}% - {evaluacion_validez_bloqueo}).")

        # Simetría general
        umbral_simetria_bloqueo = 0.7  # Cercano a 1
        simetria_promedio_bloqueo = self.data["Simetria"].mean()
        evaluacion_simetria_bloqueo = "adecuada" if simetria_promedio_bloqueo >= umbral_simetria_bloqueo else "a mejorar"
        recomendaciones.append(f"- Nivel promedio de simetría: {simetria_promedio_bloqueo:.2f} (Ideal: cercano a 1 - {evaluacion_simetria_bloqueo}).")

        return recomendaciones

    def generar_recomendaciones_recibo(self):
        """Genera recomendaciones específicas para el análisis de recibo."""
        recomendaciones = []
        columnas_necesarias = [
            "Angulo.Tronco", "Profundidad.Sentadilla",
            "Posicion.Correcta", "Contacto.Brazos",
            "Movimiento.Controlado", "Distancia.Entre.Pies"
        ]

        # Verificar columnas necesarias
        faltantes = [col for col in columnas_necesarias if col not in self.data.columns]
        if faltantes:
            recomendaciones.append(f"- Faltan las siguientes columnas: {', '.join(faltantes)}")
            return recomendaciones

        # Ángulo de tronco promedio
        rango_angulo_tronco = (20, 40)  # Grados (ejemplo de flexión hacia adelante)
        angulo_tronco_promedio = self.data["Angulo.Tronco"].mean()
        evaluacion_angulo_tronco = "adecuado" if rango_angulo_tronco[0] <= angulo_tronco_promedio <= rango_angulo_tronco[1] else "a revisar"
        recomendaciones.append(f"- Ángulo de tronco promedio: {angulo_tronco_promedio:.2f}° (Rango típico: {rango_angulo_tronco[0]}-{rango_angulo_tronco[1]}° - {evaluacion_angulo_tronco}).")

        # Profundidad de sentadilla promedio
        rango_profundidad_sentadilla = (40, 60)  # cm (ejemplo)
        profundidad_sentadilla_promedio = self.data["Profundidad.Sentadilla"].mean()
        evaluacion_profundidad_sentadilla = "adecuada" if rango_profundidad_sentadilla[0] <= profundidad_sentadilla_promedio <= rango_profundidad_sentadilla[1] else "a revisar"
        recomendaciones.append(f"- Profundidad promedio de sentadilla: {profundidad_sentadilla_promedio:.2f} cm (Rango típico: {rango_profundidad_sentadilla[0]}-{rango_profundidad_sentadilla[1]} cm - {evaluacion_profundidad_sentadilla}).")

        # Porcentaje de posición correcta
        umbral_posicion_correcta = 0.80  # 80%
        porcentaje_posicion_correcta = (self.data["Posicion.Correcta"].sum() / len(self.data)) * 100
        evaluacion_posicion = "alto" if porcentaje_posicion_correcta >= umbral_posicion_correcta * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de posiciones correctas: {porcentaje_posicion_correcta:.2f}% (Objetivo: >= {umbral_posicion_correcta * 100:.0f}% - {evaluacion_posicion}).")

        # Porcentaje de contactos de brazos
        umbral_contacto_brazos = 0.90  # 90%
        porcentaje_contacto_brazos = (self.data["Contacto.Brazos"].sum() / len(self.data)) * 100
        evaluacion_contacto_brazos = "alto" if porcentaje_contacto_brazos >= umbral_contacto_brazos * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de contactos correctos con los brazos: {porcentaje_contacto_brazos:.2f}% (Objetivo: >= {umbral_contacto_brazos * 100:.0f}% - {evaluacion_contacto_brazos}).")

        # Porcentaje de movimiento controlado
        umbral_movimiento_controlado_recibo = 0.70  # 70%
        porcentaje_movimiento_controlado = (self.data["Movimiento.Controlado"].sum() / len(self.data)) * 100
        evaluacion_movimiento_controlado = "alto" if porcentaje_movimiento_controlado >= umbral_movimiento_controlado_recibo * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de movimientos controlados: {porcentaje_movimiento_controlado:.2f}% (Objetivo: >= {umbral_movimiento_controlado_recibo * 100:.0f}% - {evaluacion_movimiento_controlado}).")

        # Distancia entre pies promedio
        rango_distancia_pies = (30, 50)  # cm (ejemplo)
        distancia_pies_promedio = self.data["Distancia.Entre.Pies"].mean()
        evaluacion_distancia_pies = "adecuada" if rango_distancia_pies[0] <= distancia_pies_promedio <= rango_distancia_pies[1] else "a revisar"
        recomendaciones.append(f"- Promedio de distancia entre pies: {distancia_pies_promedio:.2f} cm (Rango típico: {rango_distancia_pies[0]}-{rango_distancia_pies[1]} cm - {evaluacion_distancia_pies}).")

        return recomendaciones

    def generar_recomendaciones_saque(self):
        """Genera recomendaciones específicas para el análisis de saque."""
        recomendaciones = []
        columnas_necesarias = [
            "Angulo.Codo", "Altura.Brazo",
            "Alineacion.Hombro", "Alineacion.Codo",
            "Contacto.Balon", "Saque.Valido"
        ]

        # Verificar columnas necesarias
        faltantes = [col for col in columnas_necesarias if col not in self.data.columns]
        if faltantes:
            recomendaciones.append(f"- Faltan las siguientes columnas: {', '.join(faltantes)}")
            return recomendaciones

        # Ángulo de codo promedio
        rango_angulo_codo_saque = (150, 180)  # Grados (ejemplo en el momento del golpe)
        angulo_codo_promedio = self.data["Angulo.Codo"].mean()
        evaluacion_angulo_codo = "adecuado" if rango_angulo_codo_saque[0] <= angulo_codo_promedio <= rango_angulo_codo_saque[1] else "a revisar"
        recomendaciones.append(f"- Ángulo de codo promedio: {angulo_codo_promedio:.2f}° (Rango típico: {rango_angulo_codo_saque[0]}-{rango_angulo_codo_saque[1]}° - {evaluacion_angulo_codo}).")

        # Altura del brazo promedio
        altura_promedio_jugador = 180  # cm (ejemplo)
        altura_brazo_promedio = self.data["Altura.Brazo"].mean()
        altura_relativa = altura_brazo_promedio - altura_promedio_jugador / 2  # Ejemplo: relativa a la mitad de la altura
        umbral_altura_brazo = 50  # cm (ejemplo)
        evaluacion_altura_brazo = "adecuada" if altura_relativa >= umbral_altura_brazo else "a revisar"
        recomendaciones.append(f"- Altura promedio del brazo: {altura_brazo_promedio:.2f} cm (Relativa: >= {umbral_altura_brazo:.0f} cm - {evaluacion_altura_brazo}).")

        # Alineaciones promedio
        umbral_alineacion = 10  # Grados de desviación (ejemplo)
        alineacion_hombro_promedio = abs(self.data["Alineacion.Hombro"].mean())  # Asumiendo 0 es ideal
        alineacion_codo_promedio = abs(self.data["Alineacion.Codo"].mean())  # Asumiendo 0 es ideal
        recomendaciones.append(f"- Alineación promedio del hombro: {alineacion_hombro_promedio:.2f}°.")
        recomendaciones.append(f"- Alineación promedio del codo: {alineacion_codo_promedio:.2f}°.")

        # Porcentaje de contactos con balón correctos
        porcentaje_contacto_balon = (self.data["Contacto.Balon"].sum() / len(self.data)) * 100
        recomendaciones.append(f"- Porcentaje de contactos correctos con el balón: {porcentaje_contacto_balon:.2f}%.")

        # Porcentaje de saques válidos
        porcentaje_saques_validos = (self.data["Saque.Valido"].sum() / len(self.data)) * 100
        recomendaciones.append(f"- Porcentaje de saques válidos: {porcentaje_saques_validos:.2f}%.")

        # Mensaje por defecto si no hay recomendaciones específicas
        if not recomendaciones:
            recomendaciones.append("No se encontraron problemas en el análisis de saque.")

        return recomendaciones

    def generar_recomendaciones_colocador(self):
        """Genera recomendaciones específicas para el análisis de colocador."""
        recomendaciones = []
        columnas_necesarias = [
            "Angulo.Codo.Izq", "Angulo.Rodilla.Izq", "Angulo.Tronco.Izq", "Mano.Izq.Sobre.Frente",
            "Angulo.Codo.Der", "Angulo.Rodilla.Der", "Angulo.Tronco.Der", "Mano.Der.Sobre.Frente",
            "Movimiento.Controlado"
        ]

        # Verificar columnas necesarias
        faltantes = [col for col in columnas_necesarias if col not in self.data.columns]
        if faltantes:
            recomendaciones.append(f"- Faltan las siguientes columnas: {', '.join(faltantes)}")
            return recomendaciones

        # Porcentaje de manos sobre frente correctas
        umbral_manos_sobre_frente = 0.85  # 85%
        porcentaje_manos_izq = (self.data["Mano.Izq.Sobre.Frente"].sum() / len(self.data)) * 100
        porcentaje_manos_der = (self.data["Mano.Der.Sobre.Frente"].sum() / len(self.data)) * 100
        evaluacion_manos_izq = "alto" if porcentaje_manos_izq >= umbral_manos_sobre_frente * 100 else "bajo"
        evaluacion_manos_der = "alto" if porcentaje_manos_der >= umbral_manos_sobre_frente * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de manos izquierdas sobre frente: {porcentaje_manos_izq:.2f}% (Objetivo: >= {umbral_manos_sobre_frente * 100:.0f}% - {evaluacion_manos_izq}).")
        recomendaciones.append(f"- Porcentaje de manos derechas sobre frente: {porcentaje_manos_der:.2f}% (Objetivo: >= {umbral_manos_sobre_frente * 100:.0f}% - {evaluacion_manos_der}).")

        # Porcentaje de movimiento controlado
        umbral_movimiento_controlado_colocador = 0.75  # 75%
        porcentaje_movimiento_controlado = (self.data["Movimiento.Controlado"].sum() / len(self.data)) * 100
        evaluacion_movimiento_controlado = "alto" if porcentaje_movimiento_controlado >= umbral_movimiento_controlado_colocador * 100 else "bajo"
        recomendaciones.append(f"- Porcentaje de movimientos controlados: {porcentaje_movimiento_controlado:.2f}% (Objetivo: >= {umbral_movimiento_controlado_colocador * 100:.0f}% - {evaluacion_movimiento_controlado}).")

        # Simetría de ángulos de codo (promedio)
        umbral_diferencia_codo_colocador = 10  # Grados
        diferencia_media_codo = abs(self.data["Angulo.Codo.Izq"] - self.data["Angulo.Codo.Der"]).mean()
        evaluacion_codo = "buena" if diferencia_media_codo <= umbral_diferencia_codo_colocador else "a mejorar"
        recomendaciones.append(f"- Diferencia media entre ángulos de codo: {diferencia_media_codo:.2f}° (Recomendado: <= {umbral_diferencia_codo_colocador}° - {evaluacion_codo}).")

        # Simetría de ángulos de rodilla (promedio)
        umbral_diferencia_rodilla_colocador = 15  # Grados
        diferencia_media_rodilla = abs(self.data["Angulo.Rodilla.Izq"] - self.data["Angulo.Rodilla.Der"]).mean()
        evaluacion_rodilla = "buena" if diferencia_media_rodilla <= umbral_diferencia_rodilla_colocador else "a mejorar"
        recomendaciones.append(f"- Diferencia media entre ángulos de rodilla: {diferencia_media_rodilla:.2f}° (Recomendado: <= {umbral_diferencia_rodilla_colocador}° - {evaluacion_rodilla}).")

        # Simetría de ángulos de tronco (promedio)
        umbral_diferencia_tronco_colocador = 10  # Grados
        diferencia_media_tronco = abs(self.data["Angulo.Tronco.Izq"] - self.data["Angulo.Tronco.Der"]).mean()
        evaluacion_tronco = "buena" if diferencia_media_tronco <= umbral_diferencia_tronco_colocador else "a mejorar"
        recomendaciones.append(f"- Diferencia media entre ángulos de tronco: {diferencia_media_tronco:.2f}° (Recomendado: <= {umbral_diferencia_tronco_colocador}° - {evaluacion_tronco}).")

        return recomendaciones
   
    def generar_recomendaciones(self):
        """Genera un resumen con recomendaciones basadas en los análisis."""
        funciones_recomendaciones = {
            "ataque": self.generar_recomendaciones_ataque,
            "bloqueo": self.generar_recomendaciones_bloqueo,
            "recibo": self.generar_recomendaciones_recibo,
            "saque": self.generar_recomendaciones_saque,
            "colocador": self.generar_recomendaciones_colocador
        }

        funcion_recomendaciones = funciones_recomendaciones.get(self.tipo_analisis)
        if not funcion_recomendaciones:
            raise ValueError(f"Tipo de análisis no válido: {self.tipo_analisis}")

        recomendaciones = funcion_recomendaciones()
        resumen_path = self.carpeta_resultados / f"recomendaciones_{self.tipo_analisis}.txt"
        self.guardar_recomendaciones(recomendaciones, resumen_path)

    def realizar_analisis(self):
        """Realiza todo el análisis estadístico."""
        self.cargar_datos()
        self.crear_carpeta_resultados()
        self.generar_matriz_correlacion()
        self.generar_graficos_distribuciones()
        self.generar_recomendaciones()
        print(f"Análisis para {self.tipo_analisis} completado. Resultados en: {self.carpeta_resultados}")

    def generar_matriz_correlacion(self):
        """Genera y guarda una matriz de correlación."""
        if self.data.empty:
            print("No hay datos para generar la matriz de correlación.")
            return

        # Filtrar solo columnas numéricas
        df_numerico = self.data.select_dtypes(include=['number'])
        cor_matrix = df_numerico.corr()

        # Graficar y guardar la matriz
        plt.figure(figsize=(10, 8))
        sns.heatmap(cor_matrix, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Matriz de Correlación")
        plt.tight_layout()
        plt.savefig(self.carpeta_resultados / f"matriz_correlacion_{self.tipo_analisis}.png")
        plt.close()
        print("Matriz de correlación guardada.")

    def generar_graficos_distribuciones(self):
        """Genera gráficos de distribuciones por cada columna."""
        if self.data.empty:
            print("No hay datos para generar gráficos de distribuciones.")
            return

        for col in self.data.columns:
            plt.figure(figsize=(8, 5))
            sns.histplot(self.data[col], kde=True, bins=20, color="blue", alpha=0.7)
            plt.title(f"Distribución de {col}")
            plt.xlabel(col)
            plt.ylabel("Frecuencia")
            plt.grid(True)
            plt.savefig(self.carpeta_resultados / f"distribuciones_{col}_{self.tipo_analisis}.png")
            plt.close()
        print("Gráficos de distribuciones guardados.")

# -----------------------------
# PROGRAMA PRINCIPAL
# -----------------------------
def main():
    file_path = seleccionar_archivo()
    if not file_path:
        print("No se seleccionó ningún archivo. Saliendo...")
        return

    # Opciones de análisis
    opciones = ["ataque", "bloqueo", "colocador", "saque", "recibo"]
    print("Seleccione el tipo de análisis:")
    for i, opcion in enumerate(opciones, 1):
        print(f"{i}. {opcion.capitalize()}")

    try:
        seleccion = int(input("Ingrese el número de la opción: ").strip()) - 1
        if seleccion < 0 or seleccion >= len(opciones):
            raise ValueError
    except ValueError:
        print("Opción no válida. Saliendo...")
        return

    tipo_analisis = opciones[seleccion]

    # Crear instancia de la clase y realizar el análisis
    analisis = AnalisisEstadistico(file_path, tipo_analisis)
    analisis.realizar_analisis()
if __name__ == "__main__":
    main()

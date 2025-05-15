import unittest
import os
import pandas as pd
from ..main import guardar_resultados_csv
from utils.config import CSV_HEADERS  # Asegúrate de importar CSV_HEADERS correctamente

class TestGuardarResultadosCSV(unittest.TestCase):
    def setUp(self):
        """Configurar datos de prueba antes de cada test."""
        self.carpeta_salida = "Salidas"
        self.path_video = "video_prueba.mp4"
        self.deteccion = "prueba"
        self.datos = [[0, "value1", "value2"]]  # Datos de prueba con Frame y dos columnas
        self.encabezados = CSV_HEADERS.get(self.deteccion, ["Frame", "Mensajes"])

        # Crear la carpeta de salida si no existe
        os.makedirs(self.carpeta_salida, exist_ok=True)

    def tearDown(self):
        """Eliminar archivos de prueba después de cada test."""
        archivos = os.listdir(self.carpeta_salida)
        for archivo in archivos:
            if archivo.startswith("video_prueba_procesado") and archivo.endswith(".csv"):
                os.remove(os.path.join(self.carpeta_salida, archivo))

    def test_guardar_resultados_csv(self):
        """Probar que el archivo CSV se crea correctamente y contiene los datos esperados."""
        # Llamar a la función para guardar el CSV
        guardar_resultados_csv(self.datos, self.path_video, self.deteccion)

        # Verificar que el archivo CSV se haya creado
        archivos = os.listdir(self.carpeta_salida)
        archivos_csv = [f for f in archivos if f.startswith("video_prueba_procesado") and f.endswith(".csv")]
        self.assertTrue(archivos_csv, "No se generó ningún archivo CSV")

        # Cargar el archivo CSV
        filepath = os.path.join(self.carpeta_salida, archivos_csv[0])
        df = pd.read_csv(filepath)

        # Verificar que los encabezados sean correctos
        self.assertListEqual(list(df.columns), self.encabezados, "Los encabezados del CSV no coinciden.")

        # Verificar que los datos sean correctos
        for i, fila in enumerate(self.datos):
            self.assertListEqual(df.iloc[i].tolist(), fila, f"Los datos de la fila {i} no coinciden.")

if __name__ == '__main__':
    unittest.main()
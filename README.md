# DballTrainer
_Análisis técnico de acciones de voleibol mediante visión por computadora y Machine Learning_

## Índice
1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Características principales](#características-principales)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Requisitos](#requisitos)
5. [Cómo usar el Proyecto](#cómo-usar-el-proyecto)
6. [Mejoras Recientes](#mejoras-recientes)
7. [Pasos a Seguir](#pasos-a-seguir)
8. [Contribuciones](#contribuciones)
9. [Tecnologías Clave](#tecnologías-clave)
10. [Licencia](#licencia)

---

## Resumen del Proyecto

DballTrainer es una aplicación diseñada para **analizar y evaluar la postura de jugadores de voleibol** mediante el procesamiento de videos. Utiliza técnicas avanzadas de visión por computadora y modelos de detección de poses para identificar movimientos clave y generar métricas detalladas sobre la calidad técnica de cada jugada. El objetivo principal es **proporcionar retroalimentación precisa** que ayude a mejorar el rendimiento de los jugadores.

---

## Características Principales

1. **Detecciones Disponibles:**
   - **Saque:** Evaluación de la técnica de saque, incluyendo ángulos del codo, altura del brazo y alineación.
   - **Colocador:** Análisis de la postura de pase, determinando posicionamiento de brazos y estabilidad.
   - **Ataque:** Detección del remate con análisis de ángulos clave, velocidad angular y contacto con el balón.
   - **Recibo:** Evaluación de la postura defensiva, profundizando en la estabilidad y en la profundidad de la sentadilla.
   - **Bloqueo:** Evaluación de la técnica de bloqueo, considerando la extensión, altura, simetría y estabilidad.

2. **Evaluaciones Adicionales:**
   - **Estabilidad:** Análisis del centro de gravedad y posición de los pies.
   - **Contacto:** Verificación de la calidad del contacto con el balón.
   - **Salto:** Evaluación de la altura y tiempo de vuelo.
   - **Sentadillas:** Análisis de la profundidad y alineación durante la flexión de rodillas.

3. **Procesamiento en Tiempo Real:**
   - Visualización en tiempo real de las detecciones y evaluaciones.
   - Integración de un sistema de logging con niveles (INFO, WARNING, ERROR) para facilitar el diagnóstico y la depuración.

4. **Exportación de Datos y Videos Procesados:**
   - **CSV:** Los resultados se guardan automáticamente en un archivo CSV; la estructura de encabezados está centralizada en un archivo de configuración.
   - **Overlay en Video:** Opción de guardar el video procesado con las poses y etiquetas superpuestas, facilitando la revisión visual de los resultados.

5. **Detección Multipersona:**
   - Soporte para procesar videos y cámaras en escenarios de múltiples jugadores.
   - Genera un CSV por persona (hasta 6) con las acciones detectadas.
   - Utiliza el modelo **MoveNet Multipose** para identificar y rastrear múltiples jugadores simultáneamente.

---

## Estructura del Proyecto

```plaintext
pryDballTrainer/
├── detecciones/
│   ├── deteccion_saque.py
│   ├── deteccion_colocador.py
│   ├── deteccion_ataque.py
│   ├── deteccion_recibo.py
│   └── deteccion_bloqueo.py
├── evaluaciones/
│   ├── evaluar_sentadillas.py
│   ├── evaluar_contacto.py
│   ├── evaluar_estabilidad.py
│   ├── evaluar_salto.py
│   └── evaluar_pases.py
├── utils/
│   ├── video_utils.py
│   └── pose_utils.py
├── fonts/
│   └── OpenSans_Condensed-Italic.ttf
├── Salidas/
│   └── (Archivos generados: CSV y videos procesados)
├── estadistica/
│   └── (Módulos para análisis estadístico)
├── main.py
├── multi_person_detecter.py
├── requirements.txt
└── README.md
```

---

## Requisitos

### Requisitos del Sistema
- **Python:** Se recomienda usar Python 3.10 o inferior, ya que MediaPipe es compatible hasta esa versión.
- **Sistema Operativo:** Windows, macOS o Linux.

### Dependencias
Instala las bibliotecas necesarias utilizando:
```bash
python -m venv venv
source venv/bin/activate  # en Mac/Linux
venv\Scripts\activate     # en Windows
pip install -r requirements.txt
```
- mediapipe
- opencv-python
- pandas
- Pillow
- moviepy
- numpy
- matplotlib
- tensorflow

---

## Cómo Usar el Proyecto

1. **Ejecución:**
   - Asegúrate de utilizar una versión compatible de Python.
   - Ejecuta el proyecto con:
   ```bash
   python main.py
   ```

2. **Selección de Modalidad:**
   - Se mostrará un menú gráfico (Tkinter) para seleccionar entre análisis de **"Persona"** y **"Equipo"**.
   - Para **Persona**, se podrán seleccionar las diferentes detecciones.
   - Para **Equipo**, se iniciará directamente el modo multipersona, permitiendo elegir la fuente de video (archivo o cámara).

3. **Fuente de Video:**
   - Se ofrece la opción de elegir entre "Subir Video" o "Usar Cámara" mediante botones.

4. **Procesamiento y Resultados:**
   - Los resultados se muestran en tiempo real (ventana de video y consola) y se exportan a CSV según la detección seleccionada.
   - Existe la opción de guardar el video procesado con overlay para visualizar las poses y etiquetas.

---

## Mejoras Recientes

- **Validación Dinámica de Encabezados en CSV:**  
  Se implementó una validación dinámica para garantizar que los datos recopilados coincidan con los encabezados esperados para cada tipo de detección antes de guardar el archivo CSV.

- **Corrección de Errores en Tkinter:**  
  Se corrigieron errores relacionados con la inicialización de ventanas raíz (`Tk()`) en funciones que utilizan `StringVar`, como `seleccionar_deteccion`, `obtener_fuente_video` y `seleccionar_guardar_video`.

- **Estructura Dinámica de Datos:**  
  Los datos recopilados durante el procesamiento de videos ahora se estructuran dinámicamente para coincidir con los encabezados específicos de cada detección.

- **Mensajes de Error Claros:**  
  Se mejoraron los mensajes de error en caso de discrepancias entre los datos y los encabezados al guardar archivos CSV.

---

## Cómo Usar el Proyecto

### Procesamiento y Resultados

1. **Resultados en CSV:**  
   Los resultados de las detecciones se guardan automáticamente en un archivo CSV con encabezados específicos para cada tipo de detección.

2. **Validación de Datos:**  
   Antes de guardar el archivo CSV, se valida que los datos recopilados coincidan con los encabezados esperados. Si hay discrepancias, se muestra un mensaje de error claro en la consola.

3. **Mensajes en Consola:**  
   Durante el procesamiento, se muestran mensajes claros en la consola indicando si el archivo CSV se guardó correctamente o si ocurrió un error.

---

## Pasos a Seguir

1. **Pruebas Adicionales:**  
   Realizar pruebas exhaustivas para garantizar que los encabezados y los datos coincidan en todos los casos de detección.

2. **Optimización de Procesamiento:**  
   Ajustar los parámetros de MediaPipe y OpenCV para mejorar el rendimiento en tiempo real.

3. **Ampliación de Funcionalidades:**  
   Explorar la posibilidad de agregar nuevas detecciones o evaluaciones basadas en los datos recopilados.

---


## Contribuciones

Si deseas contribuir al proyecto, sigue estos pasos:
1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad:
   ```bash
   git checkout -b nueva-funcionalidad
   ```
3. Realiza tus cambios y haz un commit:
   ```bash
   git commit -m "Descripción de los cambios"
   ```
4. Envía un pull request.

---


## Tecnologías Clave
- MediaPipe: Para la detección de poses y landmarks.
- OpenCV: Para el procesamiento de imágenes y videos.
- TensorFlow: Para la integración con modelos de aprendizaje profundo como MoveNet.
- Pandas: Para la manipulación y exportación de datos en formato CSV.
- MoviePy: Para la edición y exportación de videos procesados.
- NumPy: Para cálculos matemáticos y manipulación de datos.
- Matplotlib: Para visualización de datos y gráficos.
- Scikit-learn: Para análisis estadístico y evaluaciones adicionales.


## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.
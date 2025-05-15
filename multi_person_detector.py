import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
import csv
from models.classify_pose import ClassifyPose  # Importar la clase ClassifyPose

class MultiPersonDetector:
    def __init__(self, model_url, output_dir="Salidas"):
        """
        Inicializa el detector multipersona.

        Args:
            model_url (str): URL del modelo MoveNet MultiPose en TensorFlow Hub.
            output_dir (str): Carpeta donde se guardarán los resultados.
        """
        self.model = hub.load(model_url)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # Crear la carpeta de salida si no existe
        self.pose_classifier = ClassifyPose()  # Inicializar la clase ClassifyPose

    def detect_poses(self, frame):
        """
        Detecta múltiples poses en un frame usando MoveNet MultiPose.

        Args:
            frame (numpy.ndarray): Frame de entrada en formato BGR.

        Returns:
            np.ndarray: Poses detectadas con keypoints y puntuaciones.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_image = cv2.resize(rgb_frame, (256, 256))
        input_image = tf.expand_dims(input_image, axis=0)
        input_image = tf.cast(input_image, dtype=tf.int32)
        outputs = self.model.signatures["serving_default"](input_image)
        keypoints_with_scores = outputs["output_0"].numpy()
        return keypoints_with_scores

    def save_keypoints_to_csv(self, csv_writer, keypoints_with_scores, frame_id):
        """
        Guarda los keypoints detectados en un frame en un archivo CSV.

        Args:
            csv_writer (csv.writer): Escritor CSV.
            keypoints_with_scores (np.ndarray): Keypoints detectados con puntuaciones.
            frame_id (int): Número de frame actual.
        """
        for person_id, person in enumerate(keypoints_with_scores[0]):
            keypoints = person[:51].reshape((17, 3))  # 17 puntos, cada uno con (x, y, score)
            keypoints_list = keypoints.flatten().tolist()  # Convertir a lista para ClassifyPose
            action = self.pose_classifier.classify([keypoints_list])  # Clasificar acción
            action_label = action.get(f"persona_{person_id}", "Indeterminado")

            for keypoint_id, (x, y, score) in enumerate(keypoints):
                csv_writer.writerow([frame_id, person_id, keypoint_id, x, y, score, action_label])

    def process_video_or_camera(self, source, output_video_path, output_csv_path):
        """
        Procesa un video o la cámara en tiempo real y guarda los resultados en un archivo CSV y un video.

        Args:
            source (str or int): Ruta al video o índice de la cámara (0 para cámara).
            output_video_path (str): Ruta para guardar el video procesado.
            output_csv_path (str): Ruta para guardar el archivo CSV.
        """
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("No se pudo abrir la fuente.")
            return

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

        with open(output_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["frame_id", "person_id", "keypoint_id", "x", "y", "score", "action"])  # Encabezado CSV

            frame_id = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                keypoints_with_scores = self.detect_poses(frame)
                self.save_keypoints_to_csv(writer, keypoints_with_scores, frame_id)

                # Dibujar los keypoints y las acciones en el frame
                height, width, _ = frame.shape
                for person_id, person in enumerate(keypoints_with_scores[0]):
                    keypoints = person[:51].reshape((17, 3))
                    action = self.pose_classifier.classify([keypoints.flatten().tolist()])
                    action_label = action.get(f"persona_{person_id}", "Indeterminado")

                    for x, y, score in keypoints:
                        if score > 0.5:
                            cx = int(x * width)
                            cy = int(y * height)
                            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                    # Mostrar la acción detectada en el frame
                    cv2.putText(frame, action_label, (10, 30 + person_id * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                out.write(frame)  # Guardar el frame procesado en el video
                cv2.imshow("Procesando...", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                frame_id += 1

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Video procesado guardado en: {output_video_path}")
        print(f"Keypoints guardados en: {output_csv_path}")

if __name__ == "__main__":
    # URL del modelo MoveNet MultiPose
    model_url = "https://tfhub.dev/google/movenet/multipose/lightning/1"

    # Inicializar el detector multipersona
    detector = MultiPersonDetector(model_url)

    # Configuración de entrada y salida
    source = input("Ingresa la ruta del video o '0' para usar la cámara: ").strip()
    source = 0 if source == '0' else source

    # Configurar rutas de salida en la carpeta Salidas
    output_video_path = os.path.join(detector.output_dir, "equipo_output_video.avi")
    output_csv_path = os.path.join(detector.output_dir, "equipo_output.csv")

    # Procesar el video o la cámara
    detector.process_video_or_camera(source, output_video_path, output_csv_path)

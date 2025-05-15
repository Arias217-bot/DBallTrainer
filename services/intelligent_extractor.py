import os
import json
from PIL import Image
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import openai

# ---------- CONFIGURACIÓN ----------
# Asegúrate de haber instalado:
# pip install paddleocr openai pymupdf pillow

# Inicializa el OCR de PaddleOCR (mejor calidad que Tesseract)
ocr = PaddleOCR(use_angle_cls=True, lang='es')  # lang='es' para español

# Configura tu API Key de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# ---------- EXTRACCIÓN DE TEXTO ----------
def extract_text_from_image(image_path: str) -> str:
    """Usa PaddleOCR para extraer texto de una imagen."""
    result = ocr.ocr(image_path, cls=True)
    lines = []
    for page in result:
        for line in page:
            lines.append(line[1][0])
    return "\n".join(lines)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Convierte cada página PDF a imagen y extrae texto de cada una."""
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        temp_img = f"/tmp/page_{page.number}.png"
        pix.save(temp_img)
        page_text = extract_text_from_image(temp_img)
        full_text.append(page_text)
        os.remove(temp_img)
    return "\n".join(full_text)

# ---------- PARSING INTELIGENTE ----------
def intelligent_parse(text: str) -> dict:
    """
    Usando un LLM de OpenAI, convierte texto crudo en un JSON con:
    {
      "equipo": {nombre_equipo_rival, categoria, director, asistente, director_cedula, asistente_cedula},
      "jugadores": [
          {documento, nombre, telefono, email, eps}, ...
      ]
    }
    """
    prompt = f"""
Eres un asistente experto en extraer datos de equipos de voleibol y sus jugadores.
Del siguiente texto, extrae:

- Equipo:
  • nombre_equipo_rival
  • categoria
  • director
  • asistente
  • director_cedula
  • asistente_cedula

- Lista de jugadores (pueden varias entradas):
  Para cada jugador, extrae:
  • documento
  • nombre
  • telefono
  • email
  • eps

Devuélveme solo un JSON válido con las keys "equipo" y "jugadores".

Texto:
""" + text

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # O el modelo de tu preferencia
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    content = response.choices[0].message.content.strip()
    return json.loads(content)

# ---------- DEMO DE USO ----------
if __name__ == "__main__":
    path = input("Ruta de PDF o imagen: ")
    if path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(path)
    else:
        text = extract_text_from_image(path)

    print("\n--- Texto extraído ---\n")
    print(text[:500] + '...')  # muestra un avance

    print("\n--- Parseando con LLM ---\n")
    data = intelligent_parse(text)
    print(json.dumps(data, ensure_ascii=False, indent=2))

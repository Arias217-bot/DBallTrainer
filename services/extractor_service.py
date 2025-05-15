# services/extractor_service.py
import pytesseract
# Ruta al binario de Tesseract para Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import fitz  # PyMuPDF
import re
from models.equipo_rival import EquipoRival
from models.jugadores_rivales import JugadoresRivales
from config import db
from PIL import Image


def extract_text_from_image(image_path):
    """Extrae todo el texto de una imagen usando Tesseract."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


def extract_text_from_pdf(pdf_path):
    """Extrae todo el texto de un PDF utilizando PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def safe_search(pattern, text, field_name, optional=False):
    """
    Busca una expresión regular en el texto y devuelve el grupo 1.
    Si no encuentra y es opcional, devuelve cadena vacía.
    """
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        if optional:
            return ''
        raise ValueError(f"Campo no encontrado: '{field_name}'. Verifica el formato.")
    return match.group(1).strip()

def parse_text(text):
    """
    Parsea el texto completo para extraer datos del equipo y de los jugadores.
    Usa safe_search para cada etiqueta del equipo y segmenta la sección de jugadores.
    """
    # 1. Extraer datos del equipo
    equipo = {
        'id_torneo': safe_search(r'Torneo:\s*(.*)', text, 'Torneo'),
        'nombre_equipo_rival': safe_search(r'Equipo:\s*(.*)', text, 'Equipo'),
        'categoria': safe_search(r'Categor[ií]a:\s*(.*)', text, 'Categoría'),
        'director': safe_search(r'Director T[eé]cnico:\s*(.*)', text, 'Director Técnico'),
        'asistente': safe_search(r'Asistente T[eé]cnico:\s*(.*)', text, 'Asistente Técnico'),
        'director_cedula': safe_search(r'Cedula DT:\s*(.*)', text, 'Cedula DT'),
        'asistente_cedula': safe_search(r'Cedula AT:\s*(.*)', text, 'Cedula AT'),
    }

    # 2. Subcadena de jugadores (desde primera aparición de 'Documento:')
    idx = text.lower().find('documento:')
    if idx == -1:
        raise ValueError("No se encontró la sección de jugadores. Usa 'Documento:'.")
    players_section = text[idx:]

    # 3. Dividir por cada jugador
    chunks = re.split(r'(?i)Documento:', players_section)
    jugadores = []
    for chunk in chunks:
        fragment = chunk.strip()
        if not fragment:
            continue
        sector = 'Documento:' + fragment
        # Extraer cada campo dentro del fragmento
        documento = safe_search(r'Documento:\s*(\d+)', sector, 'Documento')
        nombre = safe_search(r'Nombre:\s*([^\n\r]+)', sector, 'Nombre')
        telefono = safe_search(r'Tel[eé]fono:\s*([\d+\s-]+)', sector, 'Teléfono')
        email = safe_search(r'Email:\s*(\S+)', sector, 'Email', optional=True)
        eps = safe_search(r'EPS:\s*([^\n\r]+)', sector, 'EPS')

        jugadores.append({
            'nombre_equipo_rival': equipo['nombre_equipo_rival'],
            'documento': documento,
            'nombre': nombre,
            'telefono': telefono,
            'email': email,
            'eps': eps,
        })

    if not jugadores:
        raise ValueError("No se encontraron jugadores después del parsing. Verifica el formato de lista de jugadores.")

    return equipo, jugadores


def save_to_database(equipo_data, jugadores_data):
    """
    Inserta o actualiza el equipo y sus jugadores en la base de datos.
    """
    # Upsert del equipo
    equipo = db.session.get(EquipoRival, equipo_data['nombre_equipo_rival'])
    if not equipo:
        equipo = EquipoRival(**equipo_data)
        db.session.add(equipo)
    else:
        for key, value in equipo_data.items():
            setattr(equipo, key, value)

    # Upsert de jugadores
    for jugador_data in jugadores_data:
        jugador = db.session.get(JugadoresRivales, jugador_data['documento'])
        if not jugador:
            jugador = JugadoresRivales(**jugador_data)
            db.session.add(jugador)
        else:
            for key, value in jugador_data.items():
                setattr(jugador, key, value)

    db.session.commit()

# config/__init__.py
from flask_sqlalchemy import SQLAlchemy 

"""
    Algunas unidades simplemente no leen bien flask_sqlalchemy, vale la pena intentar si funciona apesar de que
    no se resuelva, he logrado conectarme a la base de datos aun con ese error
"""

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bd_volleyball'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print("✅ Base de datos conectada con éxito")

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANALISIS_API_URL="http://10.12.140.34:5000"
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI', 'sqlite:///default.db')

# Ruta donde se guardan los archivos temporales
UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
BACKEND_URL = 'http://localhost:5000'
ANALYZER_TIMEOUT = 60  # segundos
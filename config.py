# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANALISIS_API_URL = os.getenv('ANALISIS_API_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI', 'sqlite:///default.db')
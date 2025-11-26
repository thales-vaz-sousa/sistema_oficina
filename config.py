import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')

    # prefer DATABASE_URL (Railway). Corrige scheme se necessário.
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        password = os.getenv('DB_PASSWORD', 'TVS@2001')
        encoded_password = quote_plus(password)
        SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:{encoded_password}@localhost:5432/sistema_oficina"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
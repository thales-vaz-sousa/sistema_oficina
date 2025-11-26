import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    password = os.getenv('DB_PASSWORD', 'TVS@2001')
    encoded_password = quote_plus(password)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://postgres:{encoded_password}@localhost:5432/sistema_oficina"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False') == 'True'
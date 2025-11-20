import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = 'chave-secreta-muito-segura-aqui'
    
    # CORREÇÃO: Codificar a senha
    password = "TVS@2001"
    encoded_password = quote_plus(password)
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://postgres:{encoded_password}@localhost:5432/sistema_oficina"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Para debug - veja as queries no console
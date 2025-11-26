from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Carregar configurações
    app.config.from_object("config.Config")
    
    # Inicializar o db com o app
    db.init_app(app)
    
    # Importar e registrar rotas dentro do contexto do app
    with app.app_context():
        from app import routes
        routes.init_app(app)

    return app
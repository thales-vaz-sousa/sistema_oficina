from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object('config.Config')
    db.init_app(app)

    # criar tabelas só quando explicitamente solicitado (evita conexões automáticas em produção)
    if os.getenv('FLASK_CREATE_ALL') == '1':
        with app.app_context():
            db.create_all()

    from app.routes import init_app
    init_app(app)
    return app
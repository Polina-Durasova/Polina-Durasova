from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main_routes, auth_routes, news_routes, profile_routes
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(news_routes)
    app.register_blueprint(profile_routes)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    from . import models
    from .models import SupportOperator  # импорт после init

    with app.app_context():
        db.create_all()

        # создаём тестового оператора
        if not SupportOperator.query.filter_by(username="Example").first():
            admin = SupportOperator(
                username="Example",
                full_name="Тестовый Админ",
                password_hash=generate_password_hash("Example")
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Тестовый оператор поддержки создан: Example / Example")

    from .auth import auth_bp
    from .views import views_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)

    return app

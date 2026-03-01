import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(testing=False):
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(base_dir)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(parent_dir, 'dyslexia.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(parent_dir, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "handwriting"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "audio"), exist_ok=True)

    allowed_origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    db.init_app(app)

    from app.routes.users import users_bp
    from app.routes.handwriting import handwriting_bp
    from app.routes.speech import speech_bp
    from app.routes.results import results_bp

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(handwriting_bp, url_prefix="/api")
    app.register_blueprint(speech_bp, url_prefix="/api")
    app.register_blueprint(results_bp, url_prefix="/api")

    with app.app_context():
        from app.models import db_models  # noqa: F401
        db.create_all()

    return app

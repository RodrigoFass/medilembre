import logging
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")


def _configure_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.logger.setLevel(log_level)


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Requisição inválida"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Não autenticado"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Acesso negado"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error("Erro interno: %s", e)
        return jsonify({"error": "Erro interno do servidor"}), 500


def create_app(config_name: str = None):
    app = Flask(__name__)

    from config import config_by_name
    env = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    _configure_logging(app)
    _register_error_handlers(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:3000"])
    mail.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.patients import patients_bp
    from app.routes.medications import medications_bp
    from app.routes.doses import doses_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(patients_bp, url_prefix="/api/patients")
    app.register_blueprint(medications_bp, url_prefix="/api/medications")
    app.register_blueprint(doses_bp, url_prefix="/api/doses")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    with app.app_context():
        db.create_all()
        from app.services.scheduler import start_scheduler
        start_scheduler(app)

    app.logger.info("MediLembre iniciado no ambiente: %s", env)
    return app

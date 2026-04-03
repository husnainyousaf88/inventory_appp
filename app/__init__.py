from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # --- CORS ---
    CORS(app, resources={r"/*": {"origins": "*"}})  # allow all origins
    # ✅ For production, replace "*" with your frontend URL


    # ✅ JWT Config
    app.config["JWT_SECRET_KEY"] = "your-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # IMPORTANT FIX
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # ✅ Initialize JWT
    jwt = JWTManager(app)

    # Load models
    from app import models

    # Register blueprints
    from .routes.scan import scan_bp
    from .routes.list import list_bp
    from .routes.auth import auth_bp
    from .routes.product import product_bp

    app.register_blueprint(scan_bp)
    app.register_blueprint(list_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)

    return app
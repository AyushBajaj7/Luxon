from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
import cloudinary

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Login config
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configure Cloudinary
    cloudinary.config(secure=True)

    # Register blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.admin import admin_bp
    from app.shop import shop_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(shop_bp)

    # Import models to ensure they are registered with SQLAlchemy
    from app import models

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
        
    @app.context_processor
    def inject_global_vars():
        from app.models import Category
        if not hasattr(app, 'cached_categories'):
            # Cache category data as simple dictionaries to avoid detached session errors
            cats = Category.query.all()
            app.cached_categories = [
                {
                    'id': c.id, 
                    'name': c.name,
                    'subcategories': [{'id': s.id, 'name': s.name} for s in c.subcategories]
                } for c in cats
            ]
        return dict(categories=app.cached_categories)

    @app.after_request
    def add_header(response):
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        else:
            response.headers['Cache-Control'] = 'no-store, max-age=0'
        return response

    return app

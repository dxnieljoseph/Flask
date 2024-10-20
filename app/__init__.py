from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager  # Importer JWTManager

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True  # Activer le mode debug

    CORS(app)
    
    # Configurer la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://daniel_flask_api_db_user:XhLoZjswtNeTR9aJu3nlxAmhNCIkDZ4T@dpg-csak7q88fa8c73cpon4g-a.oregon-postgres.render.com/daniel_flask_api_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #
    
    # Clé secrète pour signer les JWT
    app.config['JWT_SECRET_KEY'] = 'votre_cle_secrete_ici'  # Utilisez une clé forte et sécurisée

    # Initialiser SQLAlchemy et Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialiser JWTManager
    jwt = JWTManager(app)  # Initialiser JWTManager

    # Importer les routes
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Swagger UI configuration
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'  # Chemin vers le fichier JSON Swagger

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI endpoint
        API_URL,  # Fichier Swagger JSON
        config={  # Config options
            'app_name': "API de Gestion des Utilisateurs"
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app

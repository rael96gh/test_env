"""
Aplicación principal con estructura organizada
"""
from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from app.config.settings import config
from app.models.swagger_models import get_models
from app.resources.health import health_ns
from app.resources.sequences import sequences_ns
from app.resources.oligos import oligos_ns

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""

    # Crear aplicación Flask
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configurar CORS
    CORS(app)

    # Configurar API con Swagger
    api = Api(
        app,
        version='1.0',
        title='Ramon ADN - Oligo Toolkit API',
        description='API profesional para análisis de secuencias de DNA y generación de oligos',
        doc='/swagger/',
        prefix='/api'
    )

    # Registrar modelos de Swagger
    models = get_models(api)

    # Registrar namespaces
    api.add_namespace(health_ns, path='/health')
    api.add_namespace(sequences_ns, path='/sequences')
    api.add_namespace(oligos_ns, path='/oligos')

    return app

def create_app_with_legacy_endpoints(config_name='default'):
    """Factory que incluye endpoints legacy para compatibilidad"""

    app = create_app(config_name)

    # Importar y registrar endpoints legacy para compatibilidad con frontend
    from app.services.legacy_compatibility import register_legacy_routes
    register_legacy_routes(app)

    return app
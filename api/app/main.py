"""
Aplicación principal con estructura organizada
"""
from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from app.config.settings import config
from app.models.swagger_models import get_models

# Import all namespaces
from app.resources.health import health_ns
from app.resources.sequences import sequences_ns
from app.resources.oligos import oligos_ns
from app.resources.mutagenesis import mutagenesis_ns
from app.resources.primers import primers_ns
from app.resources.downloads import downloads_ns
from app.resources.recycle import recycle_ns

def create_app_with_legacy_endpoints(config_name='default'):
    """Factory para crear la aplicación Flask"""

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure CORS for development - allow any localhost port
    CORS(app, origins=['http://localhost:3000', 'http://localhost', 'http://localhost:80'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)

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

    # Store models in app context for use in namespaces
    app.models = models

    # Registrar namespaces. We use a flat URL structure to match the frontend.
    api.add_namespace(health_ns, path='/health') # Keep this one separate
    api.add_namespace(sequences_ns, path='/sequences')
    api.add_namespace(oligos_ns, path='/oligos')
    api.add_namespace(mutagenesis_ns, path='/mutagenesis')
    api.add_namespace(primers_ns, path='/primers')
    api.add_namespace(downloads_ns, path='/downloads')
    api.add_namespace(recycle_ns, path='/recycle')

    return app

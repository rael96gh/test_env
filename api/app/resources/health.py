"""
Health check endpoints
"""
from flask_restx import Resource, Namespace

# Crear namespace
health_ns = Namespace('health', description='Health check operations')

@health_ns.route('/')
class Health(Resource):
    @health_ns.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'Ramon ADN - Oligo Toolkit API',
            'version': '1.0'
        }
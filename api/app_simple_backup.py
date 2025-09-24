from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Ramon ADN - Oligo Toolkit API',
    description='API para análisis de secuencias de DNA y generación de oligos',
    doc='/swagger/'
)

# Namespaces para organizar endpoints
ns_health = api.namespace('health', description='Health check operations')
ns_test = api.namespace('test', description='Test operations')

# Modelos de datos para Swagger
test_model = api.model('Test', {
    'message': fields.String(required=True, description='Test message')
})

@ns_health.route('/')
class Health(Resource):
    @ns_health.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {'status': 'healthy', 'swagger': 'working'}

@ns_test.route('/')
class Test(Resource):
    @ns_test.expect(test_model)
    @ns_test.doc('test_endpoint')
    def post(self):
        """Test endpoint for Swagger"""
        data = request.get_json()
        message = data.get('message', 'No message')
        return {'received_message': message, 'status': 'test successful'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
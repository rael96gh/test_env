"""
API organizada con Swagger funcional
"""
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import sys
import os

# Agregar directorio utils al path para imports
sys.path.append('/app/app/utils')

# Imports locales
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm

app = Flask(__name__)
CORS(app)

# Configuración de Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Ramon ADN - Oligo Toolkit API (Organizada)',
    description='API profesional para análisis de secuencias de DNA y generación de oligos',
    doc='/swagger/',
    prefix='/api'
)

# Namespaces
health_ns = Namespace('health', description='Health check operations')
sequences_ns = Namespace('sequences', description='Sequence analysis operations')

api.add_namespace(health_ns, path='/health')
api.add_namespace(sequences_ns, path='/sequences')

# Modelos
sequence_model = api.model('SequenceAnalyze', {
    'sequence': fields.String(required=True, description='DNA sequence to analyze')
})

analysis_response_model = api.model('AnalysisResponse', {
    'sequence': fields.String(description='Original sequence'),
    'reverse_complement': fields.String(description='Reverse complement'),
    'gc_content': fields.Float(description='GC content percentage'),
    'tm': fields.Float(description='Melting temperature'),
    'length': fields.Integer(description='Sequence length')
})

@health_ns.route('/')
class Health(Resource):
    @health_ns.doc('health_check')
    @health_ns.marshal_with(api.model('HealthResponse', {
        'status': fields.String(description='API status'),
        'service': fields.String(description='Service name'),
        'version': fields.String(description='API version'),
        'structure': fields.String(description='Code organization')
    }))
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'Ramon ADN - Oligo Toolkit API',
            'version': '1.0',
            'structure': 'organized'
        }

@sequences_ns.route('/analyze')
class AnalyzeSequence(Resource):
    @sequences_ns.expect(sequence_model)
    @sequences_ns.marshal_with(analysis_response_model)
    @sequences_ns.doc('analyze_sequence')
    def post(self):
        """Analyze DNA sequence properties"""
        data = request.get_json()
        sequence = data.get('sequence', '').upper().strip()

        if not sequence:
            api.abort(400, 'Sequence is required')

        try:
            reverse_complement = get_reverse_complement(sequence)
            gc_content = get_gc_content(sequence)
            tm = get_tm(sequence)

            return {
                'sequence': sequence,
                'reverse_complement': reverse_complement,
                'gc_content': gc_content,
                'tm': tm,
                'length': len(sequence)
            }
        except Exception as e:
            api.abort(500, f'Error analyzing sequence: {str(e)}')

# Endpoints de compatibilidad legacy
@app.route('/api/analyze_sequence', methods=['POST'])
def analyze_sequence_legacy():
    """Legacy endpoint para análisis de secuencia"""
    data = request.get_json()
    sequence = data.get('sequence', '')

    if not sequence:
        return jsonify({'error': 'Sequence is required'}), 400

    try:
        reverse_complement = get_reverse_complement(sequence)
        gc_content = get_gc_content(sequence)
        tm = get_tm(sequence)

        return jsonify({
            'reverse_complement': reverse_complement,
            'gc_content': gc_content,
            'tm': tm
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
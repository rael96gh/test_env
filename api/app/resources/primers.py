"""
Primer generation endpoints
"""
from flask import request, jsonify
from flask_restx import Resource, Namespace
from app.utils.primer_utils import generate_primers
from app.models.swagger_models import generate_primers_model

primers_ns = Namespace('primers', description='Primer generation operations')

@primers_ns.route('/generate')
class PrimerGeneration(Resource):
    @primers_ns.expect(generate_primers_model)
    @primers_ns.doc('generate_primers')
    def post(self):
        """Generate primers for a given sequence"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            sequence = data.get('sequence', '').strip().upper()
            options = data.get('options', {})

            if not sequence:
                return {'error': 'Sequence is required'}, 400

            result = generate_primers(sequence, options)

            return jsonify({
                'success': True,
                'primers': result
            })

        except Exception as e:
            return {'error': f'Error generating primers: {str(e)}'}, 500

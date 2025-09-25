"""
Primer generation endpoints
"""
from flask import request, jsonify
from flask_restx import Resource, Namespace
from app.utils.primer_utils import generate_primers
from app.models.swagger_models import generate_primers_model

primers_ns = Namespace('primers', description='Primer generation operations')

@primers_ns.route('/generate')
class GeneratePrimers(Resource):
    @primers_ns.expect(generate_primers_model)
    def post(self):
        data = request.get_json()
        primers = generate_primers(data['sequence'], data.get('options', {}))
        return jsonify(primers)

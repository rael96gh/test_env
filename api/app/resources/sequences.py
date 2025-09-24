"""
Sequence analysis endpoints
"""
from flask import request
from flask_restx import Resource, Namespace
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm

# Crear namespace
sequences_ns = Namespace('sequences', description='Sequence analysis operations')

@sequences_ns.route('/analyze')
class AnalyzeSequence(Resource):
    @sequences_ns.doc('analyze_sequence')
    def post(self):
        """Analyze DNA sequence properties"""
        data = request.get_json()
        sequence = data.get('sequence', '')

        if not sequence:
            return {'error': 'Sequence is required'}, 400

        try:
            reverse_complement = get_reverse_complement(sequence)
            gc_content = get_gc_content(sequence)
            tm = get_tm(sequence)

            return {
                'reverse_complement': reverse_complement,
                'gc_content': gc_content,
                'tm': tm,
                'original_sequence': sequence,
                'length': len(sequence)
            }
        except Exception as e:
            return {'error': f'Error analyzing sequence: {str(e)}'}, 500
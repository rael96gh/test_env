"""
Sequence analysis endpoints
"""
from flask import request, current_app
from flask_restx import Resource, Namespace
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm

# Crear namespace
sequences_ns = Namespace('sequences', description='Sequence analysis operations')

def get_sequence_model():
    return current_app.models.get('sequence_model')

@sequences_ns.route('/analyze')
class AnalyzeSequence(Resource):
    @sequences_ns.doc('analyze_sequence')
    def post(self):
        """Analyze DNA sequence properties"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            sequence = data.get('sequence', '').strip().upper()
            if not sequence:
                return {'error': 'Sequence is required'}, 400

            # Validate sequence contains only valid DNA characters
            valid_chars = set('ATCGWSMKRYBDHVN')
            invalid_chars = set(sequence) - valid_chars
            if invalid_chars:
                return {'error': f'Sequence contains invalid characters: {", ".join(sorted(invalid_chars))}'}, 400

            # Validate sequence length
            if len(sequence) > 50000:  # Reasonable limit
                return {'error': 'Sequence too long (maximum 50,000 characters)'}, 400

            if len(sequence) < 1:
                return {'error': 'Sequence too short'}, 400

            # Calculate sequence properties with error handling
            try:
                reverse_complement = get_reverse_complement(sequence)
                gc_content = round(get_gc_content(sequence), 2)
                tm = round(get_tm(sequence), 2)

                return {
                    'success': True,
                    'reverse_complement': reverse_complement,
                    'gc_content': gc_content,
                    'tm': tm,
                    'original_sequence': sequence,
                    'length': len(sequence)
                }
            except Exception as e:
                print(f"Error calculating sequence properties: {e}")
                return {'error': 'Error calculating sequence properties'}, 500

        except Exception as e:
            print(f"Unexpected error in sequence analysis: {e}")
            return {'error': 'An unexpected error occurred during sequence analysis'}, 500
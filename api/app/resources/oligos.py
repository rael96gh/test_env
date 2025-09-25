"""
Oligo generation endpoints
"""
from flask import request
from flask_restx import Resource, Namespace
from app.utils.sequence_utils import parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos
from app.models.swagger_models import generate_oligos_model

# Crear namespace
oligos_ns = Namespace('oligos', description='Oligo generation operations')

@oligos_ns.route('/generate')
class GenerateOligos(Resource):
    @oligos_ns.expect(generate_oligos_model)
    @oligos_ns.doc('generate_oligos')
    def post(self):
        """Generate oligos from DNA sequence"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            sequence = data.get('sequence', '').strip()
            if not sequence:
                return {'error': 'Sequence is required'}, 400

            # Validate and sanitize parameters
            try:
                oligo_length = max(10, min(200, int(data.get('oligo_length', 60))))
                overlap_length = max(5, min(100, int(data.get('overlap_length', 30))))
                gap_length = max(0, min(100, int(data.get('gap_length', 20))))
                na_conc = max(1, min(1000, int(data.get('na_conc', 50))))
                k_conc = max(0, min(1000, int(data.get('k_conc', 0))))
                oligo_conc = max(1, min(10000, int(data.get('oligo_conc', 250))))
            except (ValueError, TypeError) as e:
                return {'error': f'Invalid parameter value: {str(e)}'}, 400

            simple_oligo_maker_checked = bool(data.get('simple_oligo_maker', False))
            gapped_oligo_maker_checked = bool(data.get('gapped_oligo_maker', False))
            clean_oligos_checked = bool(data.get('clean_oligos', False))
            optimized_oligos_checked = bool(data.get('optimized_oligos', False))

            # Validate that at least one method is selected
            if not (simple_oligo_maker_checked or gapped_oligo_maker_checked):
                return {'error': 'Please select either simple or gapped oligo maker'}, 400

            # Parse FASTA sequence
            fragments = parse_multi_fasta(sequence)
            if not fragments:
                return {'error': 'Invalid FASTA sequence or no valid sequences found'}, 400

            current_oligos = []
            for fr in fragments:
                if not fr.get('seq'):
                    continue

                oligos = []
                try:
                    if gapped_oligo_maker_checked:
                        oligos = generate_gapped_oligos(fr['seq'], oligo_length, overlap_length, gap_length)
                    elif simple_oligo_maker_checked:
                        oligos = simple_oligo_maker(fr['seq'], oligo_length, overlap_length)

                    for o in oligos:
                        if o and 'sequence' in o:
                            current_oligos.append({
                                **o,
                                'fragment': fr.get('name', 'fragment')
                            })
                except Exception as e:
                    print(f"Error processing fragment {fr.get('name', 'unknown')}: {e}")
                    continue

            if not current_oligos:
                return {'error': 'No oligos could be generated from the provided sequence'}, 400

            # Apply optional processing
            try:
                if clean_oligos_checked:
                    current_oligos = clean_oligos(current_oligos)

                if optimized_oligos_checked:
                    current_oligos = optimize_oligos(current_oligos, na_conc, k_conc, oligo_conc)
            except Exception as e:
                print(f"Error in post-processing: {e}")
                # Continue with unprocessed oligos rather than failing completely

            return {
                'success': True,
                'oligos': current_oligos,
                'total_count': len(current_oligos),
                'parameters': {
                    'oligo_length': oligo_length,
                    'overlap_length': overlap_length,
                    'gap_length': gap_length,
                    'simple_oligo_maker': simple_oligo_maker_checked,
                    'gapped_oligo_maker': gapped_oligo_maker_checked,
                    'clean_oligos': clean_oligos_checked,
                    'optimized_oligos': optimized_oligos_checked
                }
            }

        except Exception as e:
            print(f"Unexpected error in oligo generation: {e}")
            return {'error': 'An unexpected error occurred during oligo generation'}, 500
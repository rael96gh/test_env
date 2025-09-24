"""
Oligo generation endpoints
"""
from flask import request
from flask_restx import Resource, Namespace
from app.utils.sequence_utils import parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos

# Crear namespace
oligos_ns = Namespace('oligos', description='Oligo generation operations')

@oligos_ns.route('/generate')
class GenerateOligos(Resource):
    @oligos_ns.doc('generate_oligos')
    def post(self):
        """Generate oligos from DNA sequence"""
        data = request.get_json()
        sequence = data.get('sequence', '')
        oligo_length = data.get('oligo_length', 60)
        overlap_length = data.get('overlap_length', 30)
        gap_length = data.get('gap_length', 20)
        na_conc = data.get('na_conc', 50)
        k_conc = data.get('k_conc', 0)
        oligo_conc = data.get('oligo_conc', 250)
        simple_oligo_maker_checked = data.get('simple_oligo_maker', False)
        gapped_oligo_maker_checked = data.get('gapped_oligo_maker', False)
        clean_oligos_checked = data.get('clean_oligos', False)
        optimized_oligos_checked = data.get('optimized_oligos', False)

        if not sequence:
            return {'error': 'Sequence is required'}, 400

        try:
            fragments = parse_multi_fasta(sequence)
            if not fragments:
                return {'error': 'Invalid FASTA sequence'}, 400

            current_oligos = []
            for fr in fragments:
                oligos = []
                if gapped_oligo_maker_checked:
                    oligos = generate_gapped_oligos(fr['seq'], oligo_length, overlap_length, gap_length)
                elif simple_oligo_maker_checked:
                    oligos = simple_oligo_maker(fr['seq'], oligo_length, overlap_length)

                for o in oligos:
                    current_oligos.append({
                        **o,
                        'fragment': fr['name']
                    })

            if clean_oligos_checked:
                current_oligos = clean_oligos(current_oligos)

            if optimized_oligos_checked:
                current_oligos = optimize_oligos(current_oligos, na_conc, k_conc, oligo_conc)

            return {
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
            return {'error': f'Error generating oligos: {str(e)}'}, 500
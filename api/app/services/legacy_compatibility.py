"""
Servicio para mantener compatibilidad con endpoints legacy
"""
from flask import request, jsonify
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm, parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos

def register_legacy_routes(app):
    """Registra rutas legacy para compatibilidad con frontend existente"""

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

    @app.route('/api/generate_oligos', methods=['POST'])
    def generate_oligos_legacy():
        """Legacy endpoint para generación de oligos"""
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
            return jsonify({'error': 'Sequence is required'}), 400

        try:
            fragments = parse_multi_fasta(sequence)
            if not fragments:
                return jsonify({'error': 'Invalid FASTA sequence'}), 400

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

            return jsonify(current_oligos)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Agregar más endpoints legacy según sea necesario
    # @app.route('/api/custom_mutagenesis', methods=['POST'])
    # @app.route('/api/saturation_mutagenesis', methods=['POST'])
    # etc.
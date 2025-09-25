"""
Mutagenesis endpoints
"""
from flask import request
from flask_restx import Resource, Namespace
from app.utils.mutagenesis_utils import generate_custom_mutagenesis, generate_saturation_mutagenesis, generate_scanning_library
from app.utils.sequence_utils import parse_multi_fasta
from app.models.swagger_models import custom_mutagenesis_model, saturation_mutagenesis_model, scanning_library_model

mutagenesis_ns = Namespace('mutagenesis', description='Mutagenesis operations')

@mutagenesis_ns.route('/custom')
class CustomMutagenesis(Resource):
    @mutagenesis_ns.expect(custom_mutagenesis_model)
    @mutagenesis_ns.doc('generate_custom_mutagenesis')
    def post(self):
        """Generate custom mutagenesis variants"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            # Validate required fields
            original_sequence = data.get('original_sequence', '').strip().upper()
            original_name = data.get('original_name', '').strip()
            mutations = data.get('mutations', [])
            generation_mode = data.get('generation_mode', 'group')

            if not original_sequence:
                return {'error': 'Original sequence is required'}, 400
            if not original_name:
                return {'error': 'Original name is required'}, 400
            if not mutations:
                return {'error': 'Mutations list is required'}, 400

            # Parse mutations (expecting format like "A123C")
            parsed_mutations = []
            for mutation in mutations:
                if isinstance(mutation, str):
                    mutation = mutation.strip()
                    if len(mutation) >= 4:  # e.g., "A123C"
                        original_aa = mutation[0]
                        new_aa = mutation[-1]
                        position = int(''.join(filter(str.isdigit, mutation)))
                        parsed_mutations.append({
                            'type': 'AA',
                            'pos': position,
                            'new': [new_aa]
                        })

            result = generate_custom_mutagenesis(original_sequence, original_name, parsed_mutations, generation_mode)

            return {
                'success': True,
                'variants': result,
                'total_count': len(result),
                'parameters': {
                    'original_sequence': original_sequence,
                    'original_name': original_name,
                    'mutations': mutations,
                    'generation_mode': generation_mode
                }
            }

        except Exception as e:
            print(f"Error in custom mutagenesis: {e}")
            return {'error': f'Error generating custom mutagenesis: {str(e)}'}, 500

@mutagenesis_ns.route('/saturation')
class SaturationMutagenesis(Resource):
    @mutagenesis_ns.expect(saturation_mutagenesis_model)
    @mutagenesis_ns.doc('generate_saturation_mutagenesis')
    def post(self):
        """Generate saturation mutagenesis variants"""
        print("=== 🧬 SATURATION MUTAGENESIS ENDPOINT CALLED - HOT RELOAD WORKING! 🧬 ===")
        try:
            data = request.get_json()

            # DEBUG: Log incoming request
            print('🔥 BACKEND - Received request data:')
            print(f'🔥 BACKEND - Raw data: {data}')
            print(f'🔥 BACKEND - Data type: {type(data)}')

            if not data:
                print('❌ BACKEND - No data received')
                return {'error': 'Request body is required'}, 400

            # Validate required fields
            fasta_content = data.get('fasta_content', '').strip()
            saturation_mutations = data.get('saturation_mutations', [])
            exclude_stops = bool(data.get('exclude_stops', False))

            # DEBUG: Log parsed fields
            print(f'🔥 BACKEND - fasta_content: {fasta_content[:100]}...' if fasta_content else '🔥 BACKEND - fasta_content: EMPTY')
            print(f'🔥 BACKEND - saturation_mutations: {saturation_mutations}')
            print(f'🔥 BACKEND - exclude_stops: {exclude_stops}')

            if not fasta_content:
                return {'error': 'FASTA content is required'}, 400
            if not saturation_mutations:
                return {'error': 'Saturation mutations list is required'}, 400

            # Parse FASTA sequences
            sequences = parse_multi_fasta(fasta_content)

            # DEBUG: Log parsed sequences
            print(f'🔥 BACKEND - Parsed sequences count: {len(sequences) if sequences else 0}')
            if sequences:
                for i, seq in enumerate(sequences):
                    print(f'🔥 BACKEND - Sequence {i}: name="{seq.get("name", "NONAME")}", length={len(seq.get("seq", ""))}')

            if not sequences:
                print('❌ BACKEND - No sequences parsed from FASTA')
                return {'error': 'No valid sequences found in FASTA content'}, 400

            # No conversion needed now - mutagenesis_utils.py handles both formats
            # Parse saturation mutations (accepting both formats)
            parsed_mutations = []
            print(f'🔥 BACKEND - Processing {len(saturation_mutations)} mutations...')

            for mutation in saturation_mutations:
                if isinstance(mutation, dict):
                    # Frontend format: {"type": "AA", "pos": 123}
                    if 'type' in mutation and 'pos' in mutation:
                        parsed_mutations.append({
                            'type': mutation['type'],
                            'pos': int(mutation['pos'])
                        })
                elif isinstance(mutation, str):
                    # String format: "123-NNN"
                    mutation = mutation.strip()
                    if '-' in mutation:
                        position_str, mutation_type = mutation.split('-', 1)
                        position = int(position_str)

                        if mutation_type.upper() == 'NNN':
                            parsed_mutations.append({
                                'type': 'AA',
                                'pos': position
                            })
                        else:
                            parsed_mutations.append({
                                'type': 'N',
                                'pos': position
                            })

            # DEBUG: Log parsed mutations
            print(f'🔥 BACKEND - Parsed mutations: {parsed_mutations}')

            if not parsed_mutations:
                print('❌ BACKEND - No valid mutations parsed')
                return {'error': 'No valid mutations found. Use format like {"type": "AA", "pos": 123} or "123-NNN"'}, 400

            # Pass sequences directly - mutagenesis_utils.py now handles both formats
            print('🔥 BACKEND - Calling generate_saturation_mutagenesis...')
            result = generate_saturation_mutagenesis(sequences, parsed_mutations, exclude_stops)

            # DEBUG: Log result
            print(f'✅ BACKEND - Generated {len(result)} variants')
            if result:
                print(f'✅ BACKEND - First variant: {result[0][:100]}...')

            response_data = {
                'success': True,
                'variants': result,
                'total_count': len(result),
                'parameters': {
                    'sequences_processed': len(sequences),
                    'mutations_applied': len(parsed_mutations),
                    'exclude_stops': exclude_stops
                }
            }

            print(f'✅ BACKEND - Sending response: success={response_data["success"]}, total_count={response_data["total_count"]}')
            return response_data

        except Exception as e:
            print(f"Error in saturation mutagenesis: {e}")
            import traceback
            traceback.print_exc()
            return {'error': f'Error generating saturation mutagenesis: {str(e)}'}, 500

@mutagenesis_ns.route('/scanning')
class ScanningLibrary(Resource):
    @mutagenesis_ns.expect(scanning_library_model)
    @mutagenesis_ns.doc('generate_scanning_library')
    def post(self):
        """Generate scanning library variants"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            # Validate required fields
            sequence = data.get('sequence', '').strip().upper()
            sequence_name = data.get('sequence_name', '').strip()
            start_position = data.get('start_position')
            end_position = data.get('end_position')
            full_sequence = bool(data.get('full_sequence', False))
            library_type = data.get('library_type', 'NNN')

            if not sequence:
                return {'error': 'Sequence is required'}, 400
            if not sequence_name:
                return {'error': 'Sequence name is required'}, 400

            # Validate positions if not full sequence
            if not full_sequence:
                if start_position is None or end_position is None:
                    return {'error': 'Start and end positions are required when full_sequence is False'}, 400

                try:
                    start_position = int(start_position)
                    end_position = int(end_position)
                except (ValueError, TypeError):
                    return {'error': 'Start and end positions must be integers'}, 400

                if start_position < 1 or end_position < start_position:
                    return {'error': 'Invalid position range'}, 400

            result = generate_scanning_library(
                sequence,
                sequence_name,
                start_position,
                end_position,
                full_sequence,
                library_type
            )

            return {
                'success': True,
                'variants': result,
                'total_count': len(result),
                'parameters': {
                    'sequence_name': sequence_name,
                    'sequence_length': len(sequence),
                    'start_position': start_position,
                    'end_position': end_position,
                    'full_sequence': full_sequence,
                    'library_type': library_type
                }
            }

        except Exception as e:
            print(f"Error in scanning library: {e}")
            return {'error': f'Error generating scanning library: {str(e)}'}, 500

"""
Oligo generation endpoints
"""
from flask import request
from flask_restx import Resource, Namespace
from app.utils.sequence_utils import parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos
from app.utils.primer_utils import generate_primers
from app.models.swagger_models import generate_oligos_model
from app.utils.recycle_utils import recycle_oligos
from app.utils.file_plate_utils import download_pooling_and_dilution_plate_files, generate_list, generate_dilution_plate_csv
import pandas as pd
import io
import zipfile
import base64
from app.utils.file_plate_utils import get_well_position
from app.utils.file_plate_utils import get_fragment_destination_map 

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
            recycle_oligos_checked = bool(data.get('recycle_oligos', False))

            # Validate that at least one method is selected
            if not (simple_oligo_maker_checked or gapped_oligo_maker_checked):
                return {'error': 'Please select either simple or gapped oligo maker'}, 400

            # Parse FASTA sequence
            fragments = parse_multi_fasta(sequence)
            if not fragments:
                return {'error': 'Invalid FASTA sequence or no valid sequences found'}, 400

            current_oligos = []
            current_primers = []
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
                    
                    primers = generate_primers(fr['seq'])
                    current_primers.append({
                        'fragment': fr.get('name', 'fragment'),
                        'name': 'forward_primer',
                        'sequence': primers['forward_primer']
                    })
                    current_primers.append({
                        'fragment': fr.get('name', 'fragment'),
                        'name': 'reverse_primer',
                        'sequence': primers['reverse_primer']
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

            recycled_pooling_data = None
            if recycle_oligos_checked:
                well_format = data.get('well_format', '96-column')
                dest_well_format = data.get('dest_well_format', '96-column')
                plate_size = int(well_format.split('-')[0])

                # Group oligos by fragment
                oligos_by_fragment = {}
                fragment_order = []
                for fr in fragments:
                    name = fr.get('name', 'fragment')
                    fragment_order.append(name)
                    oligos_by_fragment[name] = []

                for oligo in current_oligos:
                    oligos_by_fragment[oligo['fragment']].append(oligo)

                # Determine unique oligos to order and their locations
                seen_oligos_map = {}
                oligos_to_order = []
                plate_num = 1
                well_idx = 0

                for fragment_name in fragment_order:
                    for oligo in oligos_by_fragment[fragment_name]:
                        if oligo['sequence'] not in seen_oligos_map:
                            if well_idx >= plate_size:
                                well_idx = 0
                                plate_num += 1
                            
                            well_pos = get_well_position(well_idx, well_format)
                            new_location = {'Plate': f'Plate_{plate_num}', 'Well': well_pos}
                            seen_oligos_map[oligo['sequence']] = new_location
                            
                            oligos_to_order.append({
                                'Plate': new_location['Plate'],
                                'Well': new_location['Well'],
                                'Name': oligo['label'],
                                'Sequence': oligo['sequence'],
                                'Length': oligo['length']
                            })
                            well_idx += 1

                # Generate pooling instructions
                pooling_rows = []
                dest_map = get_fragment_destination_map(current_oligos, dest_well_format)
                for fragment_name in fragment_order:
                    dest = dest_map.get(fragment_name)
                    if not dest:
                        continue
                    
                    for oligo in oligos_by_fragment[fragment_name]:
                        source_location = seen_oligos_map[oligo['sequence']]
                        pooling_rows.append([
                            source_location['Plate'],
                            source_location['Well'],
                            oligo['sequence'],
                            dest['plate'],
                            dest['well'],
                            2  # Volume
                        ])

                # Create CSVs and Zip file
                oligos_to_order_df = pd.DataFrame(oligos_to_order)
                oligos_to_order_csv = oligos_to_order_df.to_csv(index=False)

                pooling_df = pd.DataFrame(pooling_rows, columns=["Plate Source", "Well Source", "Sequence", "Plate Destination", "Well Destination", "Volume Transfer"])
                reduced_pooling_csv = pooling_df.to_csv(index=False)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zf:
                    zf.writestr('oligos_to_order.csv', oligos_to_order_csv)
                    zf.writestr('reduced_pooling.csv', reduced_pooling_csv)
                
                zip_buffer.seek(0)
                recycled_pooling_data = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

                # Update current_oligos for display
                final_oligos_display = []
                seen_for_display = set()
                for fragment_name in fragment_order:
                    for oligo in oligos_by_fragment[fragment_name]:
                        if oligo['sequence'] not in seen_for_display:
                            final_oligos_display.append(oligo)
                            seen_for_display.add(oligo['sequence'])
                current_oligos = final_oligos_display

            response_data = {
                'success': True,
                'oligos': current_oligos,
                'primers': current_primers,
                'total_count': len(current_oligos),
                'parameters': {
                    'oligo_length': oligo_length,
                    'overlap_length': overlap_length,
                    'gap_length': gap_length,
                    'simple_oligo_maker': simple_oligo_maker_checked,
                    'gapped_oligo_maker': gapped_oligo_maker_checked,
                    'clean_oligos': clean_oligos_checked,
                    'optimized_oligos': optimized_oligos_checked,
                    'recycle_oligos': recycle_oligos_checked
                }
            }

            if recycled_pooling_data:
                response_data['recycled_pooling_data'] = recycled_pooling_data

            return response_data

        except Exception as e:
            print(f"Unexpected error in oligo generation: {e}")
            return {'error': 'An unexpected error occurred during oligo generation'}, 500
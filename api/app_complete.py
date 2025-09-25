"""
API completa organizada con todos los endpoints para el frontend
"""
from flask import Flask, request, jsonify, send_file
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import sys
import os
import io
import zipfile
import pandas as pd
from io import StringIO

# Correctly add the path to the 'app' directory to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Imports from the local 'app' package
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm, parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos
from app.utils.mutagenesis_utils import generate_custom_mutagenesis, generate_saturation_mutagenesis, generate_scanning_library
from app.utils.primer_utils import generate_primers
from app.utils.file_plate_utils import download_csv, download_primers_csv, download_pooling_and_dilution_plate_files

app = Flask(__name__)
CORS(app)

# API configuration with Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Ramon ADN - Oligo Toolkit API (Complete)',
    description='Complete API for DNA sequence analysis and oligo generation with all required endpoints.',
    doc='/swagger/',
    prefix='/api'
)

# Organized namespaces for different functionalities
# We will register them all at the root path '/' to match the frontend's expected URLs
health_ns = Namespace('Health', description='Health check operations')
sequences_ns = Namespace('Sequences', description='Sequence analysis operations')
oligos_ns = Namespace('Oligos', description='Oligo generation operations')
mutagenesis_ns = Namespace('Mutagenesis', description='Mutagenesis operations')
primers_ns = Namespace('Primers', description='Primer generation operations')
downloads_ns = Namespace('Downloads', description='File download operations')
recycle_ns = Namespace('Recycle', description='Oligo recycling operations')

# Register namespaces with the API at the root path
api.add_namespace(health_ns, path='/')
api.add_namespace(sequences_ns, path='/')
api.add_namespace(oligos_ns, path='/')
api.add_namespace(mutagenesis_ns, path='/')
api.add_namespace(primers_ns, path='/')
api.add_namespace(downloads_ns, path='/')
api.add_namespace(recycle_ns, path='/')


# ===== SWAGGER MODELS =====

sequence_model = api.model('SequenceAnalyze', {
    'sequence': fields.String(required=True, description='DNA sequence to analyze')
})

generate_oligos_model = api.model('GenerateOligos', {
    'sequence': fields.String(required=True, description='DNA sequence in FASTA format'),
    'oligo_length': fields.Integer(default=60, description='Oligo length'),
    'overlap_length': fields.Integer(default=30, description='Overlap length'),
    'gap_length': fields.Integer(default=20, description='Gap length for gapped oligo maker'),
    'na_conc': fields.Integer(default=50, description='Na+ concentration (mM)'),
    'k_conc': fields.Integer(default=0, description='K+ concentration (mM)'),
    'oligo_conc': fields.Integer(default=250, description='Oligo concentration (nM)'),
    'simple_oligo_maker': fields.Boolean(default=False, description='Use simple oligo maker'),
    'gapped_oligo_maker': fields.Boolean(default=False, description='Use gapped oligo maker'),
    'clean_oligos': fields.Boolean(default=False, description='Clean oligos to remove secondary structures'),
    'optimized_oligos': fields.Boolean(default=False, description='Optimize oligos for melting temperature')
})

custom_mutagenesis_model = api.model('CustomMutagenesis', {
    'original_sequence': fields.String(required=True, description='Original DNA sequence'),
    'original_name': fields.String(required=True, description='Name for the original sequence'),
    'mutations': fields.List(fields.String, required=True, description='List of mutations to apply (e.g., "A123C")'),
    'generation_mode': fields.String(default='group', enum=['group', 'individual'], description='Generation mode')
})

saturation_mutagenesis_model = api.model('SaturationMutagenesis', {
    'fasta_content': fields.String(required=True, description='Sequence in FASTA format'),
    'saturation_mutations': fields.List(fields.String, required=True, description='List of saturation mutations (e.g., "123-NNN")'),
    'exclude_stops': fields.Boolean(default=False, description='Exclude stop codons from the results')
})

scanning_library_model = api.model('ScanningLibrary', {
    'sequence': fields.String(required=True, description='DNA sequence'),
    'sequence_name': fields.String(required=True, description='Name for the sequence'),
    'start_position': fields.Integer(description='Start position for the scan'),
    'end_position': fields.Integer(description='End position for the scan'),
    'full_sequence': fields.Boolean(default=False, description='Apply to the full sequence'),
    'library_type': fields.String(default='NNN', description='Codon library type (e.g., NNN, NNK)')
})

generate_primers_model = api.model('GeneratePrimers', {
    'sequence': fields.String(required=True, description='DNA sequence for primer generation'),
    'options': fields.Raw(description='Advanced primer generation options')
})

recycle_model = api.model('RecycleOligos', {
    'fragments_csv': fields.String(required=True, description='Content of the fragments CSV file'),
    'pooling_csv': fields.String(required=True, description='Content of the pooling CSV file')
})

download_oligos_csv_model = api.model('DownloadOligosCSV', {
    'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
    'well_format': fields.String(default='96-column', description='Plate well format'),
    'sequence_name': fields.String(default='sequence', description='Base name for the output file')
})

download_primers_csv_model = api.model('DownloadPrimersCSV', {
    'generated_primers': fields.Raw(required=True, description='Dictionary of generated primers'),
    'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
    'well_format': fields.String(default='96-column', description='Source plate well format'),
    'dest_well_format': fields.String(default='96-column', description='Destination plate well format'),
    'sequence_name': fields.String(default='sequence', description='Base name for the output file')
})

download_pooling_model = api.model('DownloadPoolingFiles', {
    'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
    'well_format': fields.String(default='96-column', description='Source plate well format'),
    'dest_well_format': fields.String(default='96-column', description='Destination plate well format')
})

# ===== ENDPOINTS =====

@health_ns.route('/health')
class Health(Resource):
    @health_ns.doc('health_check')
    def get(self):
        """Provides a health check for the API."""
        return {'status': 'healthy', 'service': 'Ramon ADN - Oligo Toolkit API'}

@sequences_ns.route('/analyze_sequence')
class AnalyzeSequence(Resource):
    @sequences_ns.expect(sequence_model)
    @sequences_ns.doc('analyze_sequence')
    def post(self):
        """Analyzes a DNA sequence to calculate its reverse complement, GC content, and melting temperature (Tm)."""
        data = request.get_json()
        sequence = data.get('sequence', '').upper().strip()
        if not sequence:
            return {'error': 'Sequence is required'}, 400
        try:
            return {
                'reverse_complement': get_reverse_complement(sequence),
                'gc_content': get_gc_content(sequence),
                'tm': get_tm(sequence)
            }
        except Exception as e:
            return {'error': f'Error analyzing sequence: {str(e)}'}, 500

@oligos_ns.route('/generate_oligos')
class GenerateOligos(Resource):
    @oligos_ns.expect(generate_oligos_model)
    @oligos_ns.doc('generate_oligos')
    def post(self):
        """Generates oligos from a DNA sequence using various strategies."""
        data = request.get_json()
        if not data or 'sequence' not in data:
            return {'error': 'Request body is missing or sequence is not provided'}, 400
        
        try:
            fragments = parse_multi_fasta(data['sequence'])
            if not fragments:
                return {'error': 'Invalid or empty FASTA sequence provided'}, 400

            current_oligos = []
            for fr in fragments:
                oligos = []
                if data.get('gapped_oligo_maker'):
                    oligos = generate_gapped_oligos(fr['seq'], data.get('oligo_length', 60), data.get('overlap_length', 30), data.get('gap_length', 20))
                elif data.get('simple_oligo_maker'):
                    oligos = simple_oligo_maker(fr['seq'], data.get('oligo_length', 60), data.get('overlap_length', 30))

                for o in oligos:
                    current_oligos.append({**o, 'fragment': fr['name']})

            if data.get('clean_oligos'):
                current_oligos = clean_oligos(current_oligos)
            if data.get('optimized_oligos'):
                current_oligos = optimize_oligos(current_oligos, data.get('na_conc', 50), data.get('k_conc', 0), data.get('oligo_conc', 250))
            
            return current_oligos
        except Exception as e:
            return {'error': f'Error generating oligos: {str(e)}'}, 500

@mutagenesis_ns.route('/custom_mutagenesis')
class CustomMutagenesis(Resource):
    @mutagenesis_ns.expect(custom_mutagenesis_model)
    @mutagenesis_ns.doc('custom_mutagenesis')
    def post(self):
        """Generates custom mutations on a given DNA sequence."""
        data = request.get_json()
        if not all(k in data for k in ['original_sequence', 'original_name', 'mutations']):
            return {'error': 'Missing required fields'}, 400
        try:
            result = generate_custom_mutagenesis(data['original_sequence'], data['original_name'], data['mutations'], data.get('generation_mode', 'group'))
            return jsonify(result)
        except Exception as e:
            return {'error': f'Error in custom mutagenesis: {str(e)}'}, 500

@mutagenesis_ns.route('/saturation_mutagenesis')
class SaturationMutagenesis(Resource):
    @mutagenesis_ns.expect(saturation_mutagenesis_model)
    @mutagenesis_ns.doc('saturation_mutagenesis')
    def post(self):
        """Performs saturation mutagenesis on sequences provided in FASTA format."""
        data = request.get_json()
        if not all(k in data for k in ['fasta_content', 'saturation_mutations']):
            return {'error': 'Missing required fields'}, 400
        try:
            sequences = parse_multi_fasta(data['fasta_content'])
            if not sequences:
                return {'error': 'Invalid FASTA content'}, 400
            result = generate_saturation_mutagenesis(sequences, data['saturation_mutations'], data.get('exclude_stops', False))
            return jsonify(result)
        except Exception as e:
            return {'error': f'Error in saturation mutagenesis: {str(e)}'}, 500

@mutagenesis_ns.route('/scanning_library')
class ScanningLibrary(Resource):
    @mutagenesis_ns.expect(scanning_library_model)
    @mutagenesis_ns.doc('scanning_library')
    def post(self):
        """Creates a scanning library for a given DNA sequence."""
        data = request.get_json()
        if not all(k in data for k in ['sequence', 'sequence_name']):
            return {'error': 'Missing required fields'}, 400
        try:
            result = generate_scanning_library(data['sequence'], data['sequence_name'], data.get('start_position'), data.get('end_position'), data.get('full_sequence', False), data.get('library_type', 'NNN'))
            return jsonify(result)
        except Exception as e:
            return {'error': f'Error creating scanning library: {str(e)}'}, 500

@primers_ns.route('/generate_primers')
class GeneratePrimers(Resource):
    @primers_ns.expect(generate_primers_model)
    @primers_ns.doc('generate_primers')
    def post(self):
        """Generates primers for a given DNA sequence."""
        data = request.get_json()
        if 'sequence' not in data:
            return {'error': 'Sequence is required'}, 400
        try:
            primers = generate_primers(data['sequence'], data.get('options', {}))
            return jsonify(primers)
        except Exception as e:
            return {'error': f'Error generating primers: {str(e)}'}, 500

@downloads_ns.route('/download_oligos_csv')
class DownloadOligosCSV(Resource):
    @downloads_ns.expect(download_oligos_csv_model)
    @downloads_ns.doc('download_oligos_csv')
    def post(self):
        """Downloads generated oligos as a CSV file."""
        data = request.get_json()
        if 'generated_oligos' not in data:
            return {'error': 'Generated oligos data is required'}, 400
        try:
            csv_string = download_csv(data['generated_oligos'], data.get('well_format', '96-column'), data.get('sequence_name', 'sequence'))
            buffer = io.BytesIO(csv_string.encode('utf-8'))
            return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name=f"{data.get('sequence_name', 'sequence')}_oligos.csv")
        except Exception as e:
            return {'error': f'Error creating CSV: {str(e)}'}, 500

@downloads_ns.route('/download_primers_csv')
class DownloadPrimersCSV(Resource):
    @downloads_ns.expect(download_primers_csv_model)
    @downloads_ns.doc('download_primers_csv')
    def post(self):
        """Downloads generated primers as a CSV file."""
        data = request.get_json()
        if not all(k in data for k in ['generated_primers', 'generated_oligos']):
            return {'error': 'Missing required fields'}, 400
        try:
            csv_string = download_primers_csv(data['generated_primers'], data['generated_oligos'], data.get('well_format', '96-column'), data.get('dest_well_format', '96-column'), data.get('sequence_name', 'sequence'))
            buffer = io.BytesIO(csv_string.encode('utf-8'))
            return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name=f"{data.get('sequence_name', 'sequence')}_primers.csv")
        except Exception as e:
            return {'error': f'Error creating primers CSV: {str(e)}'}, 500

@downloads_ns.route('/download_pooling_dilution_files')
class DownloadPoolingFiles(Resource):
    @downloads_ns.expect(download_pooling_model)
    @downloads_ns.doc('download_pooling_files')
    def post(self):
        """Downloads pooling and dilution plate files as a ZIP archive."""
        data = request.get_json()
        if 'generated_oligos' not in data:
            return {'error': 'Generated oligos data is required'}, 400
        try:
            files_content = download_pooling_and_dilution_plate_files(data['generated_oligos'], data.get('well_format', '96-column'), data.get('dest_well_format', '96-column'))
            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                for filename, content in files_content.items():
                    zf.writestr(filename, content)
            memory_file.seek(0)
            return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='oligo_pooling_files.zip')
        except Exception as e:
            return {'error': f'Error creating zip file: {str(e)}'}, 500

@recycle_ns.route('/recycle')
class RecycleOligos(Resource):
    @recycle_ns.expect(recycle_model)
    @recycle_ns.doc('recycle_oligos')
    def post(self):
        """Recycles oligos from existing fragments and pooling CSV files to reduce redundancy."""
        data = request.get_json()
        if not all(k in data for k in ['fragments_csv', 'pooling_csv']):
            return {'error': 'Both fragments and pooling CSV data are required.'}, 400
        try:
            fragments_df = pd.read_csv(StringIO(data['fragments_csv']))
            pooling_df = pd.read_csv(StringIO(data['pooling_csv']))

            required_fragments_cols = {'Sequence', 'Plate', 'Well', 'Length'}
            required_pooling_cols = {'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'}

            if not required_fragments_cols.issubset(fragments_df.columns):
                 raise ValueError("Fragments CSV is missing required columns like 'Sequence', 'Plate', 'Well', 'Length'.")
            if not required_pooling_cols.issubset(pooling_df.columns):
                 raise ValueError("Pooling CSV is missing required columns like 'Plate Source', 'Well Source', etc.")

            fragments_df['Sequence'] = fragments_df['Sequence'].astype(str).str.strip().str.upper()
            deduplicated_df = fragments_df.drop_duplicates(subset=['Sequence', 'Plate'], keep='first').reset_index(drop=True)

            rows, cols = 8, 12
            max_wells_per_plate = rows * cols
            total_fragments = len(deduplicated_df)
            wells = [f"{chr(65 + i)}{c}" for c in range(1, cols + 1) for i in range(rows)]
            
            ordered_wells = [wells[i % max_wells_per_plate] for i in range(total_fragments)]
            ordered_plates = [f"Plate_{i // max_wells_per_plate + 1}" for i in range(total_fragments)]

            deduplicated_df['Ordered Source Well'] = ordered_wells
            deduplicated_df['Order Plate Source'] = ordered_plates
            
            seq_plate_map = deduplicated_df.set_index(['Sequence', 'Plate'])[['Order Plate Source', 'Ordered Source Well']].to_dict('index')

            def map_to_ordered(row):
                key = (row['Sequence'].strip().upper(), row['Plate Source'])
                return pd.Series(seq_plate_map.get(key, {'Order Plate Source': row['Plate Source'], 'Ordered Source Well': row['Well Source']}))

            pooling_df[['Ordered Plate Source', 'Ordered Well Source']] = pooling_df.apply(map_to_ordered, axis=1)
            reduced_pooling_df = pooling_df.drop_duplicates(subset=['Ordered Plate Source', 'Ordered Well Source', 'Plate Destination', 'Well Destination']).reset_index(drop=True)

            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                zf.writestr('reduced_fragments_ordered.csv', deduplicated_df.to_csv(index=False))
                zf.writestr('reduced_pooling.csv', reduced_pooling_df.to_csv(index=False))
            memory_file.seek(0)

            return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='recycled_oligos.zip')
        except Exception as e:
            return {'error': f'Error recycling oligos: {str(e)}'}, 500

if __name__ == '__main__':
    # Note: When running with Docker, host should be '0.0.0.0'
    app.run(debug=True, host='0.0.0.0', port=5001)
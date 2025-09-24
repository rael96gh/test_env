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

# Agregar directorio utils al path para imports
sys.path.append('/app/app/utils')

# Imports locales
from app.utils.sequence_utils import get_reverse_complement, get_gc_content, get_tm, parse_multi_fasta
from app.utils.oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos
from app.utils.mutagenesis_utils import generate_custom_mutagenesis, generate_saturation_mutagenesis, generate_scanning_library
from app.utils.primer_utils import generate_primers
from app.utils.file_plate_utils import download_csv, download_primers_csv, download_pooling_and_dilution_plate_files

app = Flask(__name__)
CORS(app)

# Configuración de Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Ramon ADN - Oligo Toolkit API (Completa)',
    description='API completa para análisis de secuencias de DNA y generación de oligos con todos los endpoints',
    doc='/swagger/',
    prefix='/api'
)

# Namespaces organizados
health_ns = Namespace('health', description='Health check operations')
sequences_ns = Namespace('sequences', description='Sequence analysis operations')
oligos_ns = Namespace('oligos', description='Oligo generation operations')
mutagenesis_ns = Namespace('mutagenesis', description='Mutagenesis operations')
primers_ns = Namespace('primers', description='Primer operations')
downloads_ns = Namespace('downloads', description='File download operations')
recycle_ns = Namespace('recycle', description='Recycling operations')

# Registrar namespaces
api.add_namespace(health_ns, path='/health')
api.add_namespace(sequences_ns, path='/sequences')
api.add_namespace(oligos_ns, path='/oligos')
api.add_namespace(mutagenesis_ns, path='/mutagenesis')
api.add_namespace(primers_ns, path='/primers')
api.add_namespace(downloads_ns, path='/downloads')
api.add_namespace(recycle_ns, path='/recycle')

# ===== MODELOS SWAGGER =====

# Modelos básicos
sequence_model = api.model('SequenceAnalyze', {
    'sequence': fields.String(required=True, description='DNA sequence to analyze')
})

generate_oligos_model = api.model('GenerateOligos', {
    'sequence': fields.String(required=True, description='DNA sequence'),
    'oligo_length': fields.Integer(default=60, description='Oligo length'),
    'overlap_length': fields.Integer(default=30, description='Overlap length'),
    'gap_length': fields.Integer(default=20, description='Gap length'),
    'na_conc': fields.Integer(default=50, description='Na+ concentration'),
    'k_conc': fields.Integer(default=0, description='K+ concentration'),
    'oligo_conc': fields.Integer(default=250, description='Oligo concentration'),
    'simple_oligo_maker': fields.Boolean(default=False, description='Use simple oligo maker'),
    'gapped_oligo_maker': fields.Boolean(default=False, description='Use gapped oligo maker'),
    'clean_oligos': fields.Boolean(default=False, description='Clean oligos'),
    'optimized_oligos': fields.Boolean(default=False, description='Optimize oligos')
})

custom_mutagenesis_model = api.model('CustomMutagenesis', {
    'original_sequence': fields.String(required=True, description='Original DNA sequence'),
    'original_name': fields.String(required=True, description='Original sequence name'),
    'mutations': fields.List(fields.String, required=True, description='List of mutations'),
    'generation_mode': fields.String(default='group', description='Generation mode')
})

saturation_mutagenesis_model = api.model('SaturationMutagenesis', {
    'fasta_content': fields.String(required=True, description='FASTA content'),
    'saturation_mutations': fields.List(fields.String, required=True, description='Saturation mutations'),
    'exclude_stops': fields.Boolean(default=False, description='Exclude stop codons')
})

scanning_library_model = api.model('ScanningLibrary', {
    'sequence': fields.String(required=True, description='DNA sequence'),
    'sequence_name': fields.String(required=True, description='Sequence name'),
    'start_position': fields.Integer(description='Start position'),
    'end_position': fields.Integer(description='End position'),
    'full_sequence': fields.Boolean(default=False, description='Use full sequence'),
    'library_type': fields.String(default='NNN', description='Library type')
})

generate_primers_model = api.model('GeneratePrimers', {
    'sequence': fields.String(required=True, description='DNA sequence'),
    'options': fields.Raw(description='Primer options')
})

recycle_model = api.model('RecycleOligos', {
    'fragments_csv': fields.String(required=True, description='Fragments CSV content'),
    'pooling_csv': fields.String(required=True, description='Pooling CSV content')
})

download_csv_model = api.model('DownloadCSV', {
    'generated_oligos': fields.List(fields.Raw, description='Generated oligos'),
    'well_format': fields.String(default='96-column', description='Well format'),
    'sequence_name': fields.String(default='sequence', description='Sequence name')
})

download_primers_model = api.model('DownloadPrimers', {
    'generated_primers': fields.Raw(description='Generated primers'),
    'generated_oligos': fields.List(fields.Raw, description='Generated oligos'),
    'well_format': fields.String(default='96-column', description='Well format'),
    'dest_well_format': fields.String(default='96-column', description='Destination well format'),
    'sequence_name': fields.String(default='sequence', description='Sequence name')
})

download_pooling_model = api.model('DownloadPooling', {
    'generated_oligos': fields.List(fields.Raw, description='Generated oligos'),
    'well_format': fields.String(default='96-column', description='Well format'),
    'dest_well_format': fields.String(default='96-column', description='Destination well format')
})

# ===== ENDPOINTS =====

@health_ns.route('/')
class Health(Resource):
    @health_ns.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'service': 'Ramon ADN - Oligo Toolkit API',
            'version': '1.0',
            'endpoints': 'all_complete'
        }

@sequences_ns.route('/analyze')
class AnalyzeSequence(Resource):
    @sequences_ns.expect(sequence_model)
    @sequences_ns.doc('analyze_sequence')
    def post(self):
        """Analyze DNA sequence properties"""
        data = request.get_json()
        sequence = data.get('sequence', '').upper().strip()

        if not sequence:
            return {'error': 'Sequence is required'}, 400

        try:
            reverse_complement = get_reverse_complement(sequence)
            gc_content = get_gc_content(sequence)
            tm = get_tm(sequence)

            return {
                'reverse_complement': reverse_complement,
                'gc_content': gc_content,
                'tm': tm
            }
        except Exception as e:
            return {'error': f'Error analyzing sequence: {str(e)}'}, 500

@oligos_ns.route('/generate')
class GenerateOligos(Resource):
    @oligos_ns.expect(generate_oligos_model)
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

            return current_oligos
        except Exception as e:
            return {'error': f'Error generating oligos: {str(e)}'}, 500

# Continuará en la siguiente parte...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
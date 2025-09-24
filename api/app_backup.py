from flask import Flask, request, send_file
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from sequence_utils import get_reverse_complement, get_gc_content, get_tm, parse_multi_fasta
from oligo_utils import simple_oligo_maker, generate_gapped_oligos, clean_oligos, optimize_oligos
from mutagenesis_utils import generate_custom_mutagenesis, generate_saturation_mutagenesis, generate_scanning_library
from primer_utils import generate_primers
from file_plate_utils import download_csv, download_primers_csv, download_pooling_and_dilution_plate_files, get_fragment_destination_map
import io
import zipfile
import pandas as pd
from io import StringIO

app = Flask(__name__)
CORS(app)

# Configuración de Swagger/OpenAPI
api = Api(
    app,
    version='1.0',
    title='Ramon ADN - Oligo Toolkit API',
    description='API para análisis de secuencias de DNA y generación de oligos',
    doc='/swagger/'
)

# Namespaces para organizar endpoints
ns_health = api.namespace('health', description='Health check operations')
ns_oligos = api.namespace('api/oligos', description='Oligo generation operations')
ns_mutagenesis = api.namespace('api/mutagenesis', description='Mutagenesis operations')
ns_primers = api.namespace('api/primers', description='Primer operations')
ns_recycle = api.namespace('api/recycle', description='Recycling operations')

# Modelos de datos para Swagger
sequence_analyze_model = api.model('SequenceAnalyze', {
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

mutation_model = api.model('Mutation', {
    'original_sequence': fields.String(required=True, description='Original DNA sequence'),
    'mutations': fields.List(fields.String, required=True, description='List of mutations')
})

recycle_model = api.model('Recycle', {
    'fragments_csv': fields.String(required=True, description='Fragments CSV content'),
    'pooling_csv': fields.String(required=True, description='Pooling CSV content')
})

@ns_health.route('/')
class Health(Resource):
    @ns_health.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {'status': 'healthy'}

@ns_recycle.route('/')
class RecycleAPI(Resource):
    @ns_recycle.expect(recycle_model)
    @ns_recycle.doc('recycle_oligos')
    def post(self):
        """Recycle oligos from fragments and pooling CSV files"""
        data = request.get_json()
        fragments_csv = data.get('fragments_csv')
        pooling_csv = data.get('pooling_csv')

        if not fragments_csv or not pooling_csv:
            return {'error': 'Both fragments and pooling CSV data are required.'}, 400

        try:
            fragments_df = pd.read_csv(StringIO(fragments_csv))
            if 'Sequence' not in fragments_df.columns:
                raise ValueError("The input CSV must contain a 'Sequence' column.")
            fragments_df['Sequence'] = fragments_df['Sequence'].astype(str).str.strip().str.upper()

            required_columns = {'Sequence', 'Plate', 'Well', 'Length'}
            if not required_columns.issubset(fragments_df.columns):
                raise ValueError(f"Missing required columns in fragments.csv. Expected: {required_columns}")

            deduplicated_df = fragments_df.drop_duplicates(subset=['Sequence', 'Plate'], keep='first').reset_index(drop=True)

        rows, cols = 8, 12
        max_wells_per_plate = rows * cols
        total_fragments = len(deduplicated_df)

        def generate_column_wise_wells(rows=8, cols=12):
            row_letters = [chr(65 + i) for i in range(rows)]
            col_numbers = list(range(1, cols + 1))
            return [f"{r}{c}" for c in col_numbers for r in row_letters]

        ordered_wells = []
        ordered_plates = []
        wells = generate_column_wise_wells(rows, cols)
        for i in range(total_fragments):
            plate_number = i // max_wells_per_plate + 1
            well_index = i % max_wells_per_plate
            ordered_wells.append(wells[well_index])
            ordered_plates.append(f"Plate_{plate_number}")

        deduplicated_df['Ordered Source Well'] = ordered_wells
        deduplicated_df['Order Plate Source'] = ordered_plates
        
        sequence_plate_to_ordered = deduplicated_df.set_index(['Sequence', 'Plate'])[
            ['Order Plate Source', 'Ordered Source Well']
        ].to_dict('index')

        fragments_df[['Order Plate Source', 'Ordered Source Well']] = fragments_df.apply(
            lambda row: pd.Series(sequence_plate_to_ordered.get((row['Sequence'], row['Plate']), (None, None))),
            axis=1
        )

        pooling_df = pd.read_csv(StringIO(pooling_csv))
        required_pooling_cols = {'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'}
        if not required_pooling_cols.issubset(pooling_df.columns):
            raise ValueError(f"Missing required columns in pooling.csv. Expected: {required_pooling_cols}")

        def map_to_ordered(row):
            key = (row['Sequence'].strip().upper(), row['Plate Source'])
            if key in sequence_plate_to_ordered:
                return pd.Series([
                    sequence_plate_to_ordered[key]['Order Plate Source'],
                    sequence_plate_to_ordered[key]['Ordered Source Well']
                ])
            return pd.Series([row['Plate Source'], row['Well Source']])

        pooling_df[['Ordered Plate Source', 'Ordered Well Source']] = pooling_df.apply(map_to_ordered, axis=1)

        reduced_pooling_df = pooling_df.drop_duplicates(
            subset=['Ordered Plate Source', 'Ordered Well Source', 'Plate Destination', 'Well Destination']
        ).reset_index(drop=True)

        # Create CSVs in memory
        reduced_fragments_ordered_csv = deduplicated_df.to_csv(index=False)
        reduced_pooling_csv = reduced_pooling_df.to_csv(index=False)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.writestr('reduced_fragments_ordered.csv', reduced_fragments_ordered_csv)
            zf.writestr('reduced_pooling.csv', reduced_pooling_csv)
        memory_file.seek(0)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='recycled_oligos.zip')

    except Exception as e:
        return {'error': str(e)}, 500

# Mantener compatibilidad con frontend
@app.route('/api/recycle', methods=['POST'])
def recycle_compatibility():
    """Redirect for compatibility"""
    return RecycleAPI().post()

@app.route('/api/analyze_sequence', methods=['POST'])
def analyze_sequence_compatibility():
    """Redirect for compatibility"""
    return AnalyzeSequence().post()

@app.route('/api/generate_oligos', methods=['POST'])
def generate_oligos_compatibility():
    """Redirect for compatibility"""
    return GenerateOligos().post()

@ns_oligos.route('/analyze')
class AnalyzeSequence(Resource):
    @ns_oligos.expect(sequence_analyze_model)
    @ns_oligos.doc('analyze_sequence')
    def post(self):
        """Analyze DNA sequence properties"""
        data = request.get_json()
        sequence = data.get('sequence', '')

        if not sequence:
            return {'error': 'Sequence is required'}, 400

        reverse_complement = get_reverse_complement(sequence)
        gc_content = get_gc_content(sequence)
        tm = get_tm(sequence)

        return {
            'reverse_complement': reverse_complement,
            'gc_content': gc_content,
            'tm': tm
        }

@ns_oligos.route('/generate')
class GenerateOligos(Resource):
    @ns_oligos.expect(generate_oligos_model)
    @ns_oligos.doc('generate_oligos')
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

@app.route('/api/custom_mutagenesis', methods=['POST'])
def custom_mutagenesis_api():
    data = request.get_json()
    original_sequence = data.get('original_sequence', '')
    original_name = data.get('original_name', '')
    mutations = data.get('mutations', [])
    generation_mode = data.get('generation_mode', 'group')

    if not original_sequence or not mutations:
        return jsonify({'error': 'Original sequence and mutations are required'}), 400
    
    result = generate_custom_mutagenesis(original_sequence, original_name, mutations, generation_mode)
    return jsonify(result)

@app.route('/api/saturation_mutagenesis', methods=['POST'])
def saturation_mutagenesis_api():
    data = request.get_json()
    fasta_content = data.get('fasta_content', '')
    saturation_mutations = data.get('saturation_mutations', [])
    exclude_stops = data.get('exclude_stops', False)

    if not fasta_content or not saturation_mutations:
        return jsonify({'error': 'FASTA content and saturation mutations are required'}), 400

    sequences = parse_multi_fasta(fasta_content)
    if not sequences:
        return jsonify({'error': 'Invalid FASTA content'}), 400

    result = generate_saturation_mutagenesis(sequences, saturation_mutations, exclude_stops)
    return jsonify(result)

@app.route('/api/scanning_library', methods=['POST'])
def scanning_library_api():
    data = request.get_json()
    sequence = data.get('sequence', '')
    sequence_name = data.get('sequence_name', '')
    start_position = data.get('start_position')
    end_position = data.get('end_position')
    full_sequence = data.get('full_sequence', False)
    library_type = data.get('library_type', 'NNN')

    if not sequence or not sequence_name:
        return jsonify({'error': 'Sequence and sequence name are required'}), 400

    result = generate_scanning_library(sequence, sequence_name, start_position, end_position, full_sequence, library_type)
    return jsonify(result)

@app.route('/api/generate_primers', methods=['POST'])
def generate_primers_api():
    data = request.get_json()
    sequence = data.get('sequence', '')
    options = data.get('options', {})

    if not sequence:
        return jsonify({'error': 'Sequence is required'}), 400
    
    primers = generate_primers(sequence, options)
    return jsonify(primers)

@app.route('/api/download_oligos_csv', methods=['POST'])
def download_oligos_csv_api():
    data = request.get_json()
    generated_oligos = data.get('generated_oligos', [])
    well_format = data.get('well_format', '96-column')
    sequence_name = data.get('sequence_name', 'sequence')

    csv_string = download_csv(generated_oligos, well_format, sequence_name)
    if "No oligos to download." in csv_string:
        return jsonify({'error': csv_string}), 400

    buffer = io.BytesIO()
    buffer.write(csv_string.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name=f'{sequence_name}_oligos.csv')

@app.route('/api/download_primers_csv', methods=['POST'])
def download_primers_csv_api():
    data = request.get_json()
    generated_primers = data.get('generated_primers', {})
    generated_oligos = data.get('generated_oligos', [])
    well_format = data.get('well_format', '96-column')
    dest_well_format = data.get('dest_well_format', '96-column')
    sequence_name = data.get('sequence_name', 'sequence')

    csv_string = download_primers_csv(generated_primers, generated_oligos, well_format, dest_well_format, sequence_name)
    if "No primers to download." in csv_string:
        return jsonify({'error': csv_string}), 400

    buffer = io.BytesIO()
    buffer.write(csv_string.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name=f'{sequence_name}_primers.csv')

@app.route('/api/download_pooling_dilution_files', methods=['POST'])
def download_pooling_dilution_files_api():
    data = request.get_json()
    generated_oligos = data.get('generated_oligos', [])
    well_format = data.get('well_format', '96-column')
    dest_well_format = data.get('dest_well_format', '96-column')

    files_content = download_pooling_and_dilution_plate_files(generated_oligos, well_format, dest_well_format)
    if "No oligos to download." in files_content:
        return jsonify({'error': files_content}), 400

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename, content in files_content.items():
            zf.writestr(filename, content)
    memory_file.seek(0)

    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='oligo_files.zip')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

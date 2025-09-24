"""
Modelos de datos para Swagger/OpenAPI documentation
"""
from flask_restx import fields

def get_models(api):
    """
    Retorna todos los modelos de datos para la documentación de Swagger
    """

    # Modelos básicos
    health_response_model = api.model('HealthResponse', {
        'status': fields.String(required=True, description='Status of the API')
    })

    error_response_model = api.model('ErrorResponse', {
        'error': fields.String(required=True, description='Error message')
    })

    # Modelos para análisis de secuencias
    sequence_analyze_model = api.model('SequenceAnalyze', {
        'sequence': fields.String(required=True, description='DNA sequence to analyze')
    })

    sequence_analysis_response_model = api.model('SequenceAnalysisResponse', {
        'reverse_complement': fields.String(description='Reverse complement of the sequence'),
        'gc_content': fields.Float(description='GC content percentage'),
        'tm': fields.Float(description='Melting temperature')
    })

    # Modelos para generación de oligos
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

    oligo_response_model = api.model('OligoResponse', {
        'name': fields.String(description='Oligo name'),
        'sequence': fields.String(description='Oligo sequence'),
        'length': fields.Integer(description='Oligo length'),
        'tm': fields.Float(description='Melting temperature'),
        'gc_content': fields.Float(description='GC content'),
        'fragment': fields.String(description='Fragment name')
    })

    # Modelos para mutagénesis
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

    # Modelos para primers
    primer_options_model = api.model('PrimerOptions', {
        'primer_length': fields.Integer(default=20, description='Primer length'),
        'tm_target': fields.Float(default=60.0, description='Target melting temperature')
    })

    generate_primers_model = api.model('GeneratePrimers', {
        'sequence': fields.String(required=True, description='DNA sequence'),
        'options': fields.Nested(primer_options_model, description='Primer options')
    })

    # Modelos para reciclaje
    recycle_model = api.model('RecycleOligos', {
        'fragments_csv': fields.String(required=True, description='Fragments CSV content'),
        'pooling_csv': fields.String(required=True, description='Pooling CSV content')
    })

    # Modelos para descarga de archivos
    download_csv_model = api.model('DownloadCSV', {
        'generated_oligos': fields.List(fields.Nested(oligo_response_model), description='Generated oligos'),
        'well_format': fields.String(default='96-column', description='Well format'),
        'sequence_name': fields.String(default='sequence', description='Sequence name')
    })

    return {
        'health_response': health_response_model,
        'error_response': error_response_model,
        'sequence_analyze': sequence_analyze_model,
        'sequence_analysis_response': sequence_analysis_response_model,
        'generate_oligos': generate_oligos_model,
        'oligo_response': oligo_response_model,
        'custom_mutagenesis': custom_mutagenesis_model,
        'saturation_mutagenesis': saturation_mutagenesis_model,
        'scanning_library': scanning_library_model,
        'generate_primers': generate_primers_model,
        'recycle': recycle_model,
        'download_csv': download_csv_model
    }
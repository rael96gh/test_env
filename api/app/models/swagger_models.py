"""
All Swagger models for the API
"""
from flask_restx import fields, Api

# Create a dummy Api object to define models
# This is a bit of a hack, but it allows us to define the models
# without having to pass the api object around.
api = Api()

# Models
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

def get_models(api_instance):
    """Register all models with the api instance"""
    from flask_restx import fields

    # Re-create models with the actual API instance
    sequence_model_real = api_instance.model('SequenceAnalyze', {
        'sequence': fields.String(required=True, description='DNA sequence to analyze')
    })

    generate_oligos_model_real = api_instance.model('GenerateOligos', {
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

    custom_mutagenesis_model_real = api_instance.model('CustomMutagenesis', {
        'original_sequence': fields.String(required=True, description='Original DNA sequence'),
        'original_name': fields.String(required=True, description='Name for the original sequence'),
        'mutations': fields.List(fields.String, required=True, description='List of mutations to apply (e.g., "A123C")'),
        'generation_mode': fields.String(default='group', enum=['group', 'individual'], description='Generation mode')
    })

    saturation_mutagenesis_model_real = api_instance.model('SaturationMutagenesis', {
        'fasta_content': fields.String(required=True, description='Sequence in FASTA format'),
        'saturation_mutations': fields.List(fields.String, required=True, description='List of saturation mutations (e.g., "123-NNN")'),
        'exclude_stops': fields.Boolean(default=False, description='Exclude stop codons from the results')
    })

    scanning_library_model_real = api_instance.model('ScanningLibrary', {
        'sequence': fields.String(required=True, description='DNA sequence'),
        'sequence_name': fields.String(required=True, description='Name for the sequence'),
        'start_position': fields.Integer(description='Start position for the scan'),
        'end_position': fields.Integer(description='End position for the scan'),
        'full_sequence': fields.Boolean(default=False, description='Apply to the full sequence'),
        'library_type': fields.String(default='NNN', description='Codon library type (e.g., NNN, NNK)')
    })

    generate_primers_model_real = api_instance.model('GeneratePrimers', {
        'sequence': fields.String(required=True, description='DNA sequence for primer generation'),
        'options': fields.Raw(description='Advanced primer generation options')
    })

    recycle_model_real = api_instance.model('RecycleOligos', {
        'fragments_csv': fields.String(required=True, description='Content of the fragments CSV file'),
        'pooling_csv': fields.String(required=True, description='Content of the pooling CSV file')
    })

    download_oligos_csv_model_real = api_instance.model('DownloadOligosCSV', {
        'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
        'well_format': fields.String(default='96-column', description='Plate well format'),
        'sequence_name': fields.String(default='sequence', description='Base name for the output file')
    })

    download_primers_csv_model_real = api_instance.model('DownloadPrimersCSV', {
        'generated_primers': fields.Raw(required=True, description='Dictionary of generated primers'),
        'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
        'well_format': fields.String(default='96-column', description='Source plate well format'),
        'dest_well_format': fields.String(default='96-column', description='Destination plate well format'),
        'sequence_name': fields.String(default='sequence', description='Base name for the output file')
    })

    download_pooling_model_real = api_instance.model('DownloadPoolingFiles', {
        'generated_oligos': fields.List(fields.Raw, required=True, description='List of generated oligos'),
        'well_format': fields.String(default='96-column', description='Source plate well format'),
        'dest_well_format': fields.String(default='96-column', description='Destination plate well format')
    })

    return {
        'sequence_model': sequence_model_real,
        'generate_oligos_model': generate_oligos_model_real,
        'custom_mutagenesis_model': custom_mutagenesis_model_real,
        'saturation_mutagenesis_model': saturation_mutagenesis_model_real,
        'scanning_library_model': scanning_library_model_real,
        'generate_primers_model': generate_primers_model_real,
        'recycle_model': recycle_model_real,
        'download_oligos_csv_model': download_oligos_csv_model_real,
        'download_primers_csv_model': download_primers_csv_model_real,
        'download_pooling_model': download_pooling_model_real
    }

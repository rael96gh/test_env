"""
File download endpoints
"""
from flask import request, send_file
from flask_restx import Resource, Namespace
from app.utils.file_plate_utils import download_csv, download_primers_csv, download_pooling_and_dilution_plate_files
from app.models.swagger_models import download_oligos_csv_model, download_primers_csv_model, download_pooling_model
import io
import zipfile

downloads_ns = Namespace('downloads', description='File download operations')

@downloads_ns.route('/oligos_csv')
class DownloadOligosCSV(Resource):
    @downloads_ns.expect(download_oligos_csv_model)
    @downloads_ns.doc('download_oligos_csv')
    def post(self):
        """Download generated oligos as CSV file"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            generated_oligos = data.get('generated_oligos', [])
            if not generated_oligos:
                return {'error': 'No oligos provided for download'}, 400

            well_format = data.get('well_format', '96-column')
            sequence_name = data.get('sequence_name', 'sequence')

            csv_string = download_csv(generated_oligos, well_format, sequence_name)
            buffer = io.BytesIO(csv_string.encode('utf-8'))

            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{sequence_name}_oligos.csv"
            )

        except Exception as e:
            print(f"Error in oligos CSV download: {e}")
            return {'error': f'Error generating CSV: {str(e)}'}, 500

@downloads_ns.route('/download_primers_csv')
class DownloadPrimersCSV(Resource):
    @downloads_ns.expect(download_primers_csv_model)
    @downloads_ns.doc('download_primers_csv')
    def post(self):
        """Download generated primers as CSV file"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            generated_primers = data.get('generated_primers')
            generated_oligos = data.get('generated_oligos', [])

            if not generated_primers:
                return {'error': 'No primers provided for download'}, 400
            if not generated_oligos:
                return {'error': 'No oligos provided for download'}, 400

            well_format = data.get('well_format', '96-column')
            dest_well_format = data.get('dest_well_format', '96-column')
            sequence_name = data.get('sequence_name', 'sequence')

            csv_string = download_primers_csv(
                generated_primers,
                generated_oligos,
                well_format,
                dest_well_format,
                sequence_name
            )
            buffer = io.BytesIO(csv_string.encode('utf-8'))

            return send_file(
                buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{sequence_name}_primers.csv"
            )

        except Exception as e:
            print(f"Error in primers CSV download: {e}")
            return {'error': f'Error generating primers CSV: {str(e)}'}, 500

@downloads_ns.route('/pooling_files')
class DownloadPoolingFiles(Resource):
    @downloads_ns.expect(download_pooling_model)
    @downloads_ns.doc('download_pooling_files')
    def post(self):
        """Download pooling and dilution files as ZIP"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Request body is required'}, 400

            generated_oligos = data.get('generated_oligos', [])
            if not generated_oligos:
                return {'error': 'No oligos provided for download'}, 400

            well_format = data.get('well_format', '96-column')
            dest_well_format = data.get('dest_well_format', '96-column')

            files_content = download_pooling_and_dilution_plate_files(
                generated_oligos,
                well_format,
                dest_well_format
            )

            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                for filename, content in files_content.items():
                    zf.writestr(filename, content)

            memory_file.seek(0)

            return send_file(
                memory_file,
                mimetype='application/zip',
                as_attachment=True,
                download_name='oligo_pooling_files.zip'
            )

        except Exception as e:
            print(f"Error in pooling files download: {e}")
            return {'error': f'Error generating pooling files: {str(e)}'}, 500

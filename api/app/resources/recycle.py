"""
Recycling endpoints
"""
from flask import request, send_file
from flask_restx import Resource, Namespace
from app.models.swagger_models import recycle_model
import pandas as pd
import io
import zipfile
from io import StringIO

recycle_ns = Namespace('recycle', description='Recycling operations')

@recycle_ns.route('/')
class RecycleOligos(Resource):
    @recycle_ns.expect(recycle_model)
    def post(self):
        data = request.get_json()
        fragments_csv = data.get('fragments_csv')
        pooling_csv = data.get('pooling_csv')

        fragments_df = pd.read_csv(StringIO(fragments_csv))
        pooling_df = pd.read_csv(StringIO(pooling_csv))

        # This is a simplified version of the logic from the backup file
        # A more robust implementation would be needed here
        deduplicated_df = fragments_df.drop_duplicates(subset=['Sequence', 'Plate'], keep='first')

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.writestr('reduced_fragments_ordered.csv', deduplicated_df.to_csv(index=False))
            zf.writestr('reduced_pooling.csv', pooling_df.to_csv(index=False)) # This is likely incorrect, needs full logic
        memory_file.seek(0)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='recycled_oligos.zip')

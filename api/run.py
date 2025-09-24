"""
Punto de entrada de la aplicación
"""
import os
from app.main import create_app_with_legacy_endpoints

# Crear aplicación
app = create_app_with_legacy_endpoints(
    config_name=os.environ.get('FLASK_ENV', 'default')
)

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
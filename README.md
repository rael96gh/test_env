# Ramon ADN - Oligo Toolkit

Este proyecto ha sido separado en dos contenedores Docker para mejorar la arquitectura:
- **API**: Contenedor Python con Flask para el backend
- **Frontend**: Contenedor Nginx sirviendo la aplicación web

## Estructura del Proyecto

```
ramon_adn/
├── api/                          # Contenedor API Python (Estructura Organizada)
│   ├── app/                     # Aplicación principal
│   │   ├── config/              # Configuración
│   │   │   ├── settings.py      # Configuración de Flask
│   │   │   └── constants.py     # Constantes científicas
│   │   ├── models/              # Modelos Swagger/OpenAPI
│   │   │   └── swagger_models.py
│   │   ├── resources/           # Endpoints REST organizados
│   │   │   ├── health.py        # Health check
│   │   │   ├── sequences.py     # Análisis de secuencias
│   │   │   └── oligos.py        # Generación de oligos
│   │   ├── services/            # Servicios de negocio
│   │   │   └── legacy_compatibility.py
│   │   └── utils/               # Utilidades científicas
│   │       ├── sequence_utils.py
│   │       ├── oligo_utils.py
│   │       ├── mutagenesis_utils.py
│   │       ├── primer_utils.py
│   │       └── file_plate_utils.py
│   ├── app.py                   # Punto de entrada
│   ├── requirements.txt         # Dependencias Python
│   └── Dockerfile              # Dockerfile para API
├── frontend-app/                # Contenedor Frontend
│   ├── *.html                  # Páginas web
│   ├── *.js                    # JavaScript
│   ├── *.css                   # Estilos CSS
│   └── Dockerfile              # Dockerfile para Frontend
├── docker-compose.yml          # Orquestación de contenedores
└── README.md                   # Este archivo
```

## Instrucciones de Uso

### Construir y ejecutar los contenedores

1. **Construir e iniciar los servicios:**
   ```bash
   docker-compose up --build
   ```

2. **Ejecutar en segundo plano:**
   ```bash
   docker-compose up --build -d
   ```

3. **Ver los logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Detener los servicios:**
   ```bash
   docker-compose down
   ```

### Acceso a la aplicación

- **Frontend**: http://localhost
- **API**: http://localhost:5001
- **Swagger UI**: http://localhost:5001/swagger/
- **Health check**: http://localhost:5001/health

### Desarrollo

#### Para desarrollo de la API:
```bash
cd api
pip install -r requirements.txt
python app.py
```

#### Para desarrollo del frontend:
Puedes servir los archivos HTML directamente desde `frontend-app/` con cualquier servidor web local.

## Características

- **Separación de responsabilidades**: API y Frontend en contenedores independientes
- **Documentación API**: Swagger/OpenAPI integrado con interfaz interactiva
- **Configuración de CORS**: Permite comunicación entre frontend y backend
- **Health checks**: Monitoreo de salud de los servicios
- **Red Docker**: Comunicación segura entre contenedores
- **Configuración flexible**: URLs de API configurables desde el frontend

## API Endpoints

### Nuevos Endpoints Organizados (Swagger)
- `GET /api/health/` - Health check con información del servicio
- `POST /api/sequences/analyze` - Análisis completo de secuencias DNA
- `POST /api/oligos/generate` - Generación de oligos (próximamente)
- `POST /api/mutagenesis/custom` - Mutagénesis personalizada (próximamente)

### Endpoints Legacy (Compatibilidad)
- `POST /api/analyze_sequence` - Análisis de secuencias (legacy)
- `POST /api/generate_oligos` - Generar oligos (legacy)
- `POST /api/custom_mutagenesis` - Mutagénesis personalizada (legacy)
- `POST /api/saturation_mutagenesis` - Mutagénesis de saturación (legacy)
- `POST /api/scanning_library` - Librería de barrido (legacy)
- `POST /api/generate_primers` - Generar primers (legacy)
- `POST /api/recycle` - Herramienta de reciclaje (legacy)

### Nuevas Características de la API
- **Arquitectura Modular**: Código organizado por responsabilidades
- **Documentación Swagger**: Endpoints auto-documentados
- **Validación de Datos**: Modelos definidos con validación
- **Respuestas Estructuradas**: JSON consistente y bien formateado
- **Manejo de Errores**: Códigos de estado HTTP apropiados
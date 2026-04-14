# Actividad Microsite API

API de gestión de arrendatarios y facturación de servicios (agua, luz, aseo, gas).

## 📋 Características

- ✅ API RESTful con FastAPI
- ✅ Gestión de arrendatarios (CRUD completo)
- ✅ Cálculo automático de servicios
- ✅ Generación de PDFs de comprobantes
- ✅ Descarga en ZIP de múltiples comprobantes
- ✅ Arquitectura escalable (separación de capas)
- ✅ Autenticación y limitación de tasa (rate limiting)
- ✅ Containerización con Docker
- ✅ Pipeline CI/CD con GitHub Actions
- ✅ Tests automatizados

## 🚀 Quick Start

### Requisitos Previos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Git

### Opción 1: Con Docker Compose (Recomendado)

```bash
# Clonar repositorio
git clone <repository-url>
cd Smp1-Auto

# Configurar variables de entorno
cp .env.example .env

# Iniciar servicios
docker-compose up -d

# Acceder a la API
# - API: http://localhost:8000
# - Documentación interactiva: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Opción 2: Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements-dev.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de BD

# Ejecutar tests
pytest tests/ -v

# Iniciar servidor de desarrollo
uvicorn main:app --reload

# Acceder a la API
# - API: http://localhost:8000
# - Documentación: http://localhost:8000/docs
```

## 📁 Estructura del Proyecto

```
├── models/                 # Modelos de datos (Pydantic)
│   ├── __init__.py
│   └── ClaseArrendatario.py
│
├── routes/                 # Rutas/Controladores
│   ├── __init__.py
│   ├── arrendatarios.py   # Endpoints de arrendatarios
│   └── reportes.py        # Endpoints de reportes/PDF
│
├── services/              # Lógica de negocio
│   ├── __init__.py
│   ├── arrendatario_service.py
│   ├── servicios_service.py
│   └── pdf_service.py
│
├── utils/                  # Utilidades
│   ├── __init__.py
│   ├── database.py         # Conexión a BD
│   └── constants.py        # Constantes y enumeraciones
│
├── tests/                  # Tests automatizados
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_services.py
│   └── test_endpoints.py
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # Pipeline de GitHub Actions
│
├── main.py                 # Punto de entrada
├── config.py               # Configuración
├── Dockerfile              # Containerización
├── docker-compose.yml      # Orquestación de servicios
├── requirements.txt        # Dependencias de producción
├── requirements-dev.txt    # Dependencias de desarrollo
├── .env.example            # Plantilla de variables de entorno
└── README.md
```

## 📚 API Endpoints

### Arrendatarios
- `GET /api/v1/arrendatarios/` - Obtener todos
- `POST /api/v1/arrendatarios/` - Crear nuevo
- `GET /api/v1/arrendatarios/{ubicacion}` - Obtener por ubicación
- `PUT /api/v1/arrendatarios/{id}` - Actualizar
- `DELETE /api/v1/arrendatarios/{id}` - Eliminar

### Reportes
- `POST /api/v1/preview-comprobantes/` - Previsualizar facturación
- `POST /api/v1/generar-comprobantes/` - Generar PDFs
- `POST /api/v1/generar-comprobantes-editado/` - Generar PDFs personalizados

### Health & Home
- `GET /health` - Estado de salud de la API
- `GET /` - Página principal

## ⚙️ Configuración

### Variables de Entorno

Copiar `.env.example` a `.env` y ajustar:

```env
# Base de Datos
DB_HOST=localhost
DB_USER=jhojan
DB_PASSWORD=tu_contraseña
DB_NAME=J_Arrendatarios

# Aplicación
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest tests/test_services.py -v

# Con output detallado
pytest -vv --tb=short
```

## 🏗️ Arquitectura

La aplicación sigue **Clean Architecture** con separación clara de responsabilidades:

- **Models**: Esquemas de datos con Pydantic
- **Routes**: Controladores que manejan HTTP
- **Services**: Lógica de negocio pura
- **Utils**: Funciones auxiliares (DB, constantes)

### Beneficios

✅ **Mantenibilidad**: Código limpio y organizado  
✅ **Testabilidad**: Tests unitarios e integración  
✅ **Escalabilidad**: Fácil agregar nuevas features  
✅ **Reusabilidad**: Servicios independientes de HTTP  
✅ **DevOps**: Dockerizado y con pipeline CI/CD  

## 🔐 Seguridad

- ✅ Variables de entorno enmascaradas
- ✅ Validación de entrada con Pydantic
- ✅ Rate limiting activado
- ✅ Container con usuario no-root
- ✅ CORS configurado
- ✅ Health checks para monitoreo

## 📦 Deployment

### Con Docker Compose (Desarrollo/Staging)

```bash
docker-compose up -d
```

### Manual a Producción

```bash
# Construir imagen
docker build -t smp1-api:latest .

# Push a registry
docker push your-registry/smp1-api:latest

# Ejecutar
docker run -d \
  -e DB_HOST=prod-db.example.com \
  -e DB_PASSWORD=<secret> \
  -p 8000:8000 \
  smp1-api:latest
```

## 🔄 Pipeline CI/CD

GitHub Actions ejecuta automáticamente:

1. **Linting**: Pylint + Black
2. **Type checking**: Mypy
3. **Tests**: Pytest con cobertura
4. **Build**: Construcción de Docker image
5. **Deploy**: Push a registry (si está en main)

Ver `.github/workflows/ci-cd.yml` para detalles.

## 📝 Cambios de la v1 a v2

- ✅ Arquitectura propia refactorizada (Models → Routes → Services → Utils)
- ✅ Logging centralizado
- ✅ Configuración por entorno
- ✅ Tests automatizados
- ✅ Containerización con Docker
- ✅ Pipeline CI/CD
- ✅ Endpoints versionados `/api/v1/`

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver [LICENCE.md](LICENCE.md) para más detalles.

## 👥 Soporte

Para soporte e issues, abrir un ticket en GitHub Issues.

---

**Versión**: 2.0.0  
**Última actualización**: 2024-12-20


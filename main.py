"""
Actividad Microsite API - Main Application
FastAPI application for managing tenants (arrendatarios) and utility billing.
"""
import logging
import os
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address

# Import configuration
from config import ALLOWED_ORIGINS, DEBUG, LOG_LEVEL

# Import routers
from routes.arrendatarios import router as arrendatarios_router
from routes.reportes import router as reportes_router
from routes.legacy import router as legacy_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="Actividad Microsite API",
    description="API for managing tenants and utility billing",
    version="2.0.0"
)

# Apply rate limiter to app
app.state.limiter = limiter

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if services directory exists
try:
    app.mount("/services", StaticFiles(directory="services"), name="services")
except Exception as e:
    logger.warning(f"Could not mount services directory: {e}")

try:
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
except Exception as e:
    logger.warning(f"Could not mount frontend assets directory: {e}")

# Include routers
app.include_router(arrendatarios_router)
app.include_router(reportes_router)
app.include_router(legacy_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "2.0.0"}


# Home endpoint
@app.get("/", tags=["Home"])
async def read_root():
    """Serve the modern frontend build with fallback to legacy HTML."""
    try:
        modern_index = "static/index.html"
        if os.path.exists(modern_index):
            return FileResponse(modern_index)

        if os.path.exists("J0.html"):
            return FileResponse("J0.html")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home page not found"
        )
    except Exception as e:
        logger.error(f"Error reading home page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading home page"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=LOG_LEVEL.lower(),
        reload=DEBUG
    )




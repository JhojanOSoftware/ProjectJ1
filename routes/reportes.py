"""Route handlers for reporting and PDF generation endpoints."""
from fastapi import APIRouter, HTTPException, status, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import logging

from models.ClaseArrendatario import PDFData
from services.servicios_service import ServiciosService
from services.pdf_service import PDFService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["reportes"])


@router.post("/preview-comprobantes/")
async def preview_comprobantes(
    agua_valor: float = Form(...),
    luz_valor: float = Form(...),
    aseo_valor: float = Form(...),
    gas_valor: float = Form(...),
    ubicacion: str = Form(...)
):
    """
    Preview service charges for a location.
    
    Returns breakdown of all charges for each tenant.
    """
    try:
        preview_data = ServiciosService.build_preview(
            agua_valor, luz_valor, aseo_valor, gas_valor, ubicacion
        )
        return JSONResponse(content=preview_data)
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating preview: {str(e)}"
        )


@router.post("/generar-comprobantes/")
async def generar_comprobantes(
    agua_valor: float = Form(...),
    luz_valor: float = Form(...),
    aseo_valor: float = Form(...),
    gas_valor: float = Form(...),
    ubicacion: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate PDF receipts for all tenants in a location.
    
    Returns a ZIP file with all receipts.
    """
    try:
        # Build preview first to get all data
        preview = ServiciosService.build_preview(
            agua_valor, luz_valor, aseo_valor, gas_valor, ubicacion
        )
        
        # Convert preview data to format needed for PDF generation
        personas_list = []
        for arr in preview["arrendatarios"]:
            personas_list.append({
                "nombre": arr["nombre_arrendatario"],
                "ubicacion": arr["nombre_ubicacion"],
                "direccion": arr["direccion_ubicacion"],
                "personas_por_arrendatario": arr["personas_por_arrendatario"],
                "servicios": arr["servicios"],
                "servicios_extra": arr.get("servicios_extra")
            })
        
        # Generate PDFs
        zip_path, archive_files = PDFService.generar_multiples_pdfs(personas_list)
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(PDFService.cleanup_temp_files, [zip_path.rsplit('/', 1)[0]])
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.split('/')[-1]
        )
    except Exception as e:
        logger.error(f"Error generating comprobantes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDFs: {str(e)}"
        )


@router.post("/generar-comprobantes-editado/")
async def generar_comprobantes_editado(
    datos: PDFData,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate PDF receipts from manually edited data.
    
    Accepts custom service data for each person.
    Returns a ZIP file with all receipts.
    """
    try:
        # Convert PersonaEditada models to dict format
        personas_list = []
        for persona in datos.personas:
            servicios_dict = {}
            for servicio in persona.servicios:
                valor = servicio.valor if servicio.valor is not None else 0
                servicios_dict[servicio.descripcion.lower()] = valor
            
            personas_list.append({
                "nombre": persona.nombre,
                "ubicacion": persona.ubicacion,
                "direccion": persona.direccion,
                "personas_por_arrendatario": persona.personas_por_arrendatario or 1,
                "servicios": servicios_dict,
                "servicios_extra": [c.dict() for c in (persona.servicios_extra or [])]
            })
        
        # Generate PDFs
        zip_path, archive_files = PDFService.generar_multiples_pdfs(personas_list)
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(PDFService.cleanup_temp_files, [zip_path.rsplit('/', 1)[0]])
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.split('/')[-1]
        )
    except Exception as e:
        logger.error(f"Error generating edited comprobantes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDFs: {str(e)}"
        )


@router.post("/generar_pdf_editado/")
async def generar_pdf_editado_legacy_alias(
    datos: PDFData,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Legacy alias for older frontend calls that still use snake_case."""
    return await generar_comprobantes_editado(datos=datos, background_tasks=background_tasks)

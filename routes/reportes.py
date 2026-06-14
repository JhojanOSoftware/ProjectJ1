"""Route handlers for reporting and PDF generation endpoints."""
from fastapi import APIRouter, HTTPException, status, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import logging

from models.ClaseArrendatario import PDFData
from services.servicios_service import ServiciosService
from services.pdf_service import PDFService
from services.recibo_service import ReciboService

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


@router.post("/guardar-historial-recibos/")
async def guardar_historial_recibos(
    personas: list,
    mes: int,
    anio: int
):
    """
    Save receipt history after successful PDF generation.
    
    This endpoint stores receipt data in database for historical tracking.
    
    Args:
        personas: List of person dicts with: nombre, id, ubicacion, direccion,
                 personas_por_arrendatario, servicios (dict), servicios_extra (list)
        mes: Month (1-12)
        anio: Year
    """
    try:
        if not personas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No personas provided"
            )
        
        if mes < 1 or mes > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month (1-12)"
            )
        
        # Convert personas to proper format with id_arrendatario
        personas_formatted = []
        for p in personas:
            personas_formatted.append({
                "id_arrendatario": p.get("id"),
                "nombre": p.get("nombre"),
                "ubicacion": p.get("ubicacion"),
                "direccion": p.get("direccion"),
                "personas_por_arrendatario": p.get("personas_por_arrendatario", 1),
                "servicios": p.get("servicios", {}),
                "servicios_extra": p.get("servicios_extra", [])
            })
        
        success = ReciboService.guardar_historial_recibos(personas_formatted, mes, anio)
        
        if success:
            return {
                "status": "success",
                "message": f"Historial guardado para {len(personas)} arrendatarios",
                "mes": mes,
                "anio": anio
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving receipt history"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving receipt history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving receipt history: {str(e)}"
        )


@router.get("/listar-recibos/")
async def listar_recibos(
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    id_arrendatario: Optional[int] = None,
    nombre_arrendatario: Optional[str] = None
):
    """
    List receipt history with optional filters.
    
    Args:
        mes: Filter by month (1-12)
        anio: Filter by year
        id_arrendatario: Filter by tenant ID
        nombre_arrendatario: Search by tenant name (partial)
    """
    try:
        recibos = ReciboService.listar_recibos(
            mes=mes,
            anio=anio,
            id_arrendatario=id_arrendatario,
            nombre_arrendatario=nombre_arrendatario
        )
        
        return {
            "status": "success",
            "total": len(recibos),
            "recibos": recibos
        }
    except Exception as e:
        logger.error(f"Error listing receipts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing receipts: {str(e)}"
        )


@router.get("/detalle-recibo/{id_recibo}")
async def detalle_recibo(id_recibo: int):
    """Get detailed information for a specific receipt."""
    try:
        detalle = ReciboService.obtener_detalle_recibo(id_recibo)
        
        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        return {
            "status": "success",
            "recibo": detalle
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting receipt detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting receipt detail: {str(e)}"
        )


@router.get("/meses-disponibles/")
async def meses_disponibles(anio: Optional[int] = None):
    """Get available months with receipt data."""
    try:
        meses = ReciboService.obtener_meses_disponibles(anio=anio)
        
        return {
            "status": "success",
            "meses": meses
        }
    except Exception as e:
        logger.error(f"Error getting available months: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available months: {str(e)}"
        )


@router.get("/anos-disponibles/")
async def anos_disponibles():
    """Get available years with receipt data."""
    try:
        anos = ReciboService.obtener_anos_disponibles()
        
        return {
            "status": "success",
            "anos": anos
        }
    except Exception as e:
        logger.error(f"Error getting available years: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available years: {str(e)}"
        )

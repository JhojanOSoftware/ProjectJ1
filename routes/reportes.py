"""Route handlers for reporting and PDF generation endpoints."""
import os
import base64
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Form, BackgroundTasks, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from models.ClaseArrendatario import PDFData
from services.servicios_service import ServiciosService
from services.pdf_service import PDFService
from services.recibo_service import ReciboService

logger = logging.getLogger(__name__)

# Standard router with prefix /api/v1
router = APIRouter(prefix="/api/v1", tags=["reportes"])

# Router for /api path prefix to support both /api/recibos and /api/v1/recibos
router_recibos = APIRouter(prefix="/api", tags=["recibos"])


# Pydantic models for receipt history storage
class ReciboDetalleSchema(BaseModel):
    concepto: str
    monto: float

class ReciboSchema(BaseModel):
    id_arrendatario: int
    nombre_arrendatario: str
    monto_total: float
    pdf_base64: str
    detalle: List[ReciboDetalleSchema]

class GuardarRecibosRequest(BaseModel):
    mes: str
    anio: int
    recibos: List[ReciboSchema]


def helper_encode_pdfs_response(zip_path: str, archive_files: List[str], personas_list: List[dict]) -> dict:
    """Helper to convert generated ZIP and PDFs to base64 response."""
    try:
        # Encode ZIP file
        with open(zip_path, "rb") as f:
            zip_base64 = base64.b64encode(f.read()).decode("utf-8")
            
        # Encode individual PDFs
        pdfs_response = []
        for i, persona in enumerate(personas_list):
            if i < len(archive_files):
                file_path = archive_files[i]
                with open(file_path, "rb") as f:
                    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
                pdfs_response.append({
                    "id_arrendatario": persona.get("id_arrendatario") or persona.get("id") or 0,
                    "nombre_arrendatario": persona.get("nombre", ""),
                    "pdf_base64": pdf_b64
                })
        return {
            "zip_base64": zip_base64,
            "pdfs": pdf_response_list_format(pdfs_response, personas_list)
        }
    except Exception as e:
        logger.error(f"Error encoding files to base64: {e}")
        raise

def pdf_response_list_format(pdfs_response: List[dict], personas_list: List[dict]) -> List[dict]:
    # Ensure order matches
    return pdfs_response


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
    
    Returns ZIP base64 and list of individual PDFs in base64.
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
                "id_arrendatario": arr["id_arrendatario"],
                "nombre": arr["nombre_arrendatario"],
                "ubicacion": arr["nombre_ubicacion"],
                "direccion": arr["direccion_ubicacion"],
                "personas_por_arrendatario": arr["personas_por_arrendatario"],
                "servicios": arr["servicios"],
                "servicios_extra": arr.get("servicios_extra")
            })
        
        # Generate PDFs
        zip_path, archive_files = PDFService.generar_multiples_pdfs(personas_list)
        
        # Build Base64 JSON response
        response_data = helper_encode_pdfs_response(zip_path, archive_files, personas_list)
        
        # Schedule cleanup of temp files
        if background_tasks:
            background_tasks.add_task(PDFService.cleanup_temp_files, [zip_path.rsplit('/', 1)[0]])
            
        return JSONResponse(content=response_data)
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
    
    Returns ZIP base64 and list of individual PDFs in base64.
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
                "id_arrendatario": persona.id,
                "nombre": persona.nombre,
                "ubicacion": persona.ubicacion,
                "direccion": persona.direccion,
                "personas_por_arrendatario": persona.personas_por_arrendatario or 1,
                "servicios": servicios_dict,
                "servicios_extra": [c.dict() for c in (persona.servicios_extra or [])]
            })
        
        # Generate PDFs
        zip_path, archive_files = PDFService.generar_multiples_pdfs(personas_list)
        
        # Build Base64 JSON response
        response_data = helper_encode_pdfs_response(zip_path, archive_files, personas_list)
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(PDFService.cleanup_temp_files, [zip_path.rsplit('/', 1)[0]])
            
        return JSONResponse(content=response_data)
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


# --- HISTORICAL RECEIPTS ENDPOINTS ---

async def handle_guardar_recibos(data: GuardarRecibosRequest):
    try:
        recibos_list = []
        for r in data.recibos:
            recibos_list.append({
                "id_arrendatario": r.id_arrendatario,
                "nombre_arrendatario": r.nombre_arrendatario,
                "monto_total": r.monto_total,
                "pdf_base64": r.pdf_base64,
                "detalle": [{"concepto": d.concepto, "monto": d.monto} for d in r.detalle]
            })
        success = ReciboService.guardar_historial_recibos(recibos_list, data.mes, data.anio)
        if success:
            return {"success": True}
        else:
            return {"error": "No se pudo guardar el histórico en la base de datos"}
    except Exception as e:
        logger.error(f"Error saving historical receipts: {e}")
        return {"error": str(e)}

async def handle_query_recibos(
    mes: Optional[str] = None,
    anio: Optional[int] = None,
    id_arrendatario: Optional[int] = None
):
    try:
        recibos = ReciboService.listar_recibos(mes=mes, anio=anio, id_arrendatario=id_arrendatario)
        return {"recibos": recibos}
    except Exception as e:
        logger.error(f"Error listing historical receipts: {e}")
        return {"error": str(e)}

async def handle_descargar_pdf(id_recibo: int):
    try:
        res = ReciboService.obtener_pdf_recibo(id_recibo)
        if not res:
            raise HTTPException(status_code=404, detail="Recibo no encontrado")
        
        nombre_arrendatario, pdf_base64 = res
        if not pdf_base64:
            raise HTTPException(status_code=404, detail="PDF no disponible en la base de datos")
            
        pdf_bytes = base64.b64decode(pdf_base64)
        safe_name = nombre_arrendatario.replace(" ", "_").replace("/", "_")
        filename = f"recibo_{safe_name}_{id_recibo}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving PDF bytes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Register endpoints under both prefixes /api and /api/v1
@router_recibos.post("/recibos/guardar")
async def api_guardar_recibos(data: GuardarRecibosRequest):
    res = await handle_guardar_recibos(data)
    if "error" in res:
        return JSONResponse(status_code=500, content=res)
    return res

@router.post("/recibos/guardar")
async def api_v1_guardar_recibos(data: GuardarRecibosRequest):
    res = await handle_guardar_recibos(data)
    if "error" in res:
        return JSONResponse(status_code=500, content=res)
    return res

@router_recibos.get("/recibos")
async def api_query_recibos(
    mes: Optional[str] = None,
    anio: Optional[int] = None,
    id_arrendatario: Optional[int] = None
):
    res = await handle_query_recibos(mes, anio, id_arrendatario)
    if isinstance(res, dict) and "error" in res:
        return JSONResponse(status_code=500, content=res)
    return res

@router.get("/recibos")
async def api_v1_query_recibos(
    mes: Optional[str] = None,
    anio: Optional[int] = None,
    id_arrendatario: Optional[int] = None
):
    res = await handle_query_recibos(mes, anio, id_arrendatario)
    if isinstance(res, dict) and "error" in res:
        return JSONResponse(status_code=500, content=res)
    return res

@router_recibos.get("/recibos/{id_recibo}/pdf")
async def api_descargar_pdf(id_recibo: int):
    return await handle_descargar_pdf(id_recibo)

@router.get("/recibos/{id_recibo}/pdf")
async def api_v1_descargar_pdf(id_recibo: int):
    return await handle_descargar_pdf(id_recibo)

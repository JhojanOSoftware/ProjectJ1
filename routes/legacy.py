"""Legacy compatibility routes for old frontend paths.

These endpoints keep the application backward compatible while the frontend
is transitioned to the versioned /api/v1 routes.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse

from models.ClaseArrendatario import Arrendatario, ArrendatarioUpdate, PDFData
from services.arrendatario_service import ArrendatarioService
from services.servicios_service import ServiciosService
from services.pdf_service import PDFService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["legacy"])


@router.get("/Arrendatarios/")
async def obtener_arrendatarios():
    """Legacy endpoint that returns all arrendatarios."""
    try:
        arrendatarios = ArrendatarioService.get_all_arrendatarios()
        return {"data": arrendatarios}
    except Exception as e:
        logger.error(f"Error obteniendo arrendatarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo arrendatarios: {str(e)}"
        )


@router.post("/Arrendatarios/", status_code=status.HTTP_201_CREATED)
async def crear_proyecto(arrendatario: Arrendatario):
    """Legacy endpoint for creating an arrendatario."""
    try:
        result = ArrendatarioService.create_arrendatario(arrendatario)
        return {"message": "Proyecto creado correctamente", "id": result["id"], "data": arrendatario.dict()}
    except Exception as e:
        logger.error(f"Error creando proyecto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando proyecto: {str(e)}"
        )


@router.get("/Arrendatarios/{nombre_ubicacion}")
async def obtener_arrendatario(nombre_ubicacion: str):
    """Legacy endpoint that returns tenants by location."""
    try:
        arrendatarios = ArrendatarioService.get_arrendatarios_by_location(nombre_ubicacion)
        return {"data": arrendatarios}
    except Exception as e:
        logger.error(f"Error obteniendo arrendatarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo arrendatarios: {str(e)}"
        )


@router.put("/api/v1/update_data_db/")
async def actualizar_arrendatario(arrendatario_id: int, datos: ArrendatarioUpdate):
    """Legacy update endpoint used by the existing frontend."""
    try:
        success = ArrendatarioService.update_arrendatario(arrendatario_id, datos)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrendatario no encontrado"
            )
        return {"message": "Arrendatario actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando arrendatario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando arrendatario: {str(e)}"
        )


@router.delete("/Arrendatarios/{arrendatario_id}")
async def eliminar_arrendatario(arrendatario_id: int):
    """Legacy delete endpoint."""
    try:
        success = ArrendatarioService.delete_arrendatario(arrendatario_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arrendatario no encontrado"
            )
        return {"message": "Arrendatario eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando arrendatario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando arrendatario: {str(e)}"
        )


@router.post("/PreviewComprobantes/")
async def preview_comprobante_end_point(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Selecionador: str = Form(...)
):
    """Legacy preview endpoint used by the existing frontend."""
    try:
        data = ServiciosService.build_preview(WaterValue, LuzValue, AseoValue, GasValue, Selecionador)
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error generando preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando preview: {str(e)}"
        )


@router.post("/GenerarComprobantes/")
async def generar_comprobante_end_point(
    WaterValue: int = Form(...),
    LuzValue: int = Form(...),
    AseoValue: int = Form(...),
    GasValue: int = Form(...),
    Selecionador: str = Form(...),
    backg: BackgroundTasks = BackgroundTasks()
):
    """Legacy ZIP-generation endpoint used by the existing frontend."""
    try:
        preview = ServiciosService.build_preview(WaterValue, LuzValue, AseoValue, GasValue, Selecionador)

        personas_list = []
        for entry in preview["arrendatarios"]:
            personas_list.append(
                {
                    "nombre": entry["nombre_arrendatario"],
                    "ubicacion": entry["nombre_ubicacion"],
                    "direccion": entry["direccion_ubicacion"],
                    "personas_por_arrendatario": entry["personas_por_arrendatario"],
                    "servicios": entry["servicios"],
                    "servicios_extra": entry.get("servicios_extra")
                }
            )

        zip_path, _ = PDFService.generar_multiples_pdfs(personas_list)
        if backg:
            backg.add_task(PDFService.cleanup_temp_files, [zip_path.rsplit('/', 1)[0]])

        return FileResponse(zip_path, media_type="application/zip", filename=zip_path.split('/')[-1])
    except Exception as e:
        logger.error(f"Error generando comprobantes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando PDFs: {str(e)}"
        )



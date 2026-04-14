"""Route handlers for arrendatario endpoints."""
from fastapi import APIRouter, HTTPException, status
import logging

from models.ClaseArrendatario import Arrendatario, ArrendatarioUpdate
from services.arrendatario_service import ArrendatarioService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/arrendatarios", tags=["arrendatarios"])


@router.get("/")
async def get_all_arrendatarios():
    """Get all arrendatarios."""
    try:
        arrendatarios = ArrendatarioService.get_all_arrendatarios()
        return {"data": arrendatarios}
    except Exception as e:
        logger.error(f"Error in get_all_arrendatarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching arrendatarios: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_arrendatario(arrendatario: Arrendatario):
    """Create a new arrendatario."""
    try:
        result = ArrendatarioService.create_arrendatario(arrendatario)
        return {
            "message": "Arrendatario created successfully",
            "id": result["id"],
            "data": arrendatario.dict()
        }
    except Exception as e:
        logger.error(f"Error creating arrendatario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating arrendatario: {str(e)}"
        )


@router.get("/{nombre_ubicacion}")
async def get_arrendatarios_by_location(nombre_ubicacion: str):
    """Get all arrendatarios for a specific location."""
    try:
        arrendatarios = ArrendatarioService.get_arrendatarios_by_location(nombre_ubicacion)
        if not arrendatarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No arrendatarios found for location: {nombre_ubicacion}"
            )
        return {"data": arrendatarios}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching arrendatarios for {nombre_ubicacion}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching arrendatarios: {str(e)}"
        )


@router.put("/{arrendatario_id}")
async def update_arrendatario(arrendatario_id: int, datos: ArrendatarioUpdate):
    """Update an existing arrendatario."""
    try:
        success = ArrendatarioService.update_arrendatario(arrendatario_id, datos)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arrendatario with ID {arrendatario_id} not found"
            )
        return {"message": "Arrendatario updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating arrendatario {arrendatario_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating arrendatario: {str(e)}"
        )


@router.delete("/{arrendatario_id}", status_code=status.HTTP_200_OK)
async def delete_arrendatario(arrendatario_id: int):
    """Delete an arrendatario."""
    try:
        success = ArrendatarioService.delete_arrendatario(arrendatario_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arrendatario with ID {arrendatario_id} not found"
            )
        return {"message": "Arrendatario deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting arrendatario {arrendatario_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting arrendatario: {str(e)}"
        )

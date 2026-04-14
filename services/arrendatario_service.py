"""Business logic for Arrendatario (tenant) operations."""
import logging
from typing import List, Dict, Optional
from utils.database import get_db_context
from models.ClaseArrendatario import Arrendatario, ArrendatarioUpdate

logger = logging.getLogger(__name__)


class ArrendatarioService:
    """Service for managing arrendatarios (tenants) in the database."""
    
    @staticmethod
    def get_all_arrendatarios() -> List[Dict]:
        """Retrieve all arrendatarios from the database."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM arrendatarios_J0")
                rows = cur.fetchall()
                return rows
        except Exception as e:
            logger.error(f"Error fetching all arrendatarios: {e}")
            raise
    
    @staticmethod
    def get_arrendatarios_by_location(nombre_ubicacion: str) -> List[Dict]:
        """Get all arrendatarios for a specific location."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, nombre_arrendatario, nombre_ubicacion, "
                    "direccion_ubicacion, personas_por_arrendatario "
                    "FROM arrendatarios_J0 WHERE nombre_ubicacion = %s",
                    (nombre_ubicacion,)
                )
                rows = cur.fetchall()
                return rows
        except Exception as e:
            logger.error(f"Error fetching arrendatarios for {nombre_ubicacion}: {e}")
            raise
    
    @staticmethod
    def get_total_personas(nombre_ubicacion: str) -> int:
        """Get total number of people in a location."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT SUM(personas_por_arrendatario) as total "
                    "FROM arrendatarios_J0 WHERE nombre_ubicacion = %s",
                    (nombre_ubicacion,)
                )
                row = cur.fetchone()
                total = row["total"] if row and row["total"] is not None else 1
                return max(1, total)  # Minimum 1 to avoid division by zero
        except Exception as e:
            logger.error(f"Error calculating total personas: {e}")
            raise
    
    @staticmethod
    def get_count_arrendatarios(nombre_ubicacion: str) -> int:
        """Get count of arrendatarios in a location."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT COUNT(*) as count FROM arrendatarios_J0 "
                    "WHERE nombre_ubicacion = %s",
                    (nombre_ubicacion,)
                )
                row = cur.fetchone()
                return row["count"] if row else 0
        except Exception as e:
            logger.error(f"Error counting arrendatarios: {e}")
            raise
    
    @staticmethod
    def create_arrendatario(arrendatario: Arrendatario) -> Dict:
        """Create a new arrendatario in the database."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO arrendatarios_J0 
                    (nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,
                     personas_por_arrendatario, telefono, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        arrendatario.nombre_arrendatario,
                        arrendatario.nombre_ubicacion,
                        arrendatario.direccion_ubicacion,
                        arrendatario.personas_por_arrendatario,
                        arrendatario.telefono,
                        arrendatario.email
                    )
                )
                conn.commit()
                new_id = cur.lastrowid
                logger.info(f"Created arrendatario with ID: {new_id}")
                return {"id": new_id, "message": "Arrendatario created successfully"}
        except Exception as e:
            logger.error(f"Error creating arrendatario: {e}")
            raise
    
    @staticmethod
    def update_arrendatario(arrendatario_id: int, datos: ArrendatarioUpdate) -> bool:
        """Update an existing arrendatario."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                # Check if exists
                cur.execute("SELECT * FROM arrendatarios_J0 WHERE id = %s", (arrendatario_id,))
                if not cur.fetchone():
                    return False
                
                # Update
                cur.execute(
                    """
                    UPDATE arrendatarios_J0 
                    SET nombre_arrendatario = %s, nombre_ubicacion = %s, 
                        direccion_ubicacion = %s, personas_por_arrendatario = %s, 
                        telefono = %s, email = %s
                    WHERE id = %s
                    """,
                    (
                        datos.nombre_arrendatario,
                        datos.nombre_ubicacion,
                        datos.direccion_ubicacion,
                        datos.personas_por_arrendatario,
                        datos.telefono,
                        datos.email,
                        arrendatario_id
                    )
                )
                conn.commit()
                logger.info(f"Updated arrendatario ID: {arrendatario_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating arrendatario {arrendatario_id}: {e}")
            raise
    
    @staticmethod
    def delete_arrendatario(arrendatario_id: int) -> bool:
        """Delete an arrendatario from the database."""
        try:
            with get_db_context() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM arrendatarios_J0 WHERE id = %s", (arrendatario_id,))
                conn.commit()
                affected = cur.rowcount
                if affected > 0:
                    logger.info(f"Deleted arrendatario ID: {arrendatario_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting arrendatario {arrendatario_id}: {e}")
            raise

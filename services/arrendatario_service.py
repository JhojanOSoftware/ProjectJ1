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
                for r in rows:
                    if 'servicios_extra' in r and r['servicios_extra'] and isinstance(r['servicios_extra'], str):
                        try:
                            import json
                            r['servicios_extra'] = json.loads(r['servicios_extra'])
                        except Exception:
                            pass
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
                # Use SELECT * to be tolerant to schema additions (e.g., servicios_extra)
                cur.execute(
                    "SELECT * FROM arrendatarios_J0 WHERE nombre_ubicacion = %s",
                    (nombre_ubicacion,)
                )
                rows = cur.fetchall()
                # Parse servicios_extra JSON if present as string
                for r in rows:
                    if 'servicios_extra' in r and r['servicios_extra'] and isinstance(r['servicios_extra'], str):
                        try:
                            import json
                            r['servicios_extra'] = json.loads(r['servicios_extra'])
                        except Exception:
                            # leave as-is if parsing fails
                            pass
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
                next_id = None
                import json
                servicios_extra_json = None
                if getattr(arrendatario, 'servicios_extra', None) is not None:
                    try:
                        servicios_extra_json = json.dumps([c.dict() if hasattr(c, 'dict') else c for c in arrendatario.servicios_extra])
                    except Exception:
                        servicios_extra_json = None

                try:
                    cur.execute(
                        """
                        INSERT INTO arrendatarios_J0 
                        (nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,
                         personas_por_arrendatario, telefono, email, in_house_location, servicios_extra)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            arrendatario.nombre_arrendatario,
                            arrendatario.nombre_ubicacion,
                            arrendatario.direccion_ubicacion,
                            arrendatario.personas_por_arrendatario,
                            arrendatario.telefono,
                            arrendatario.email,
                            arrendatario.in_house_location,
                            servicios_extra_json
                        )
                    )
                except Exception as db_error:
                    # Handle two cases: missing servicios_extra column or missing id default
                    err_code = getattr(db_error, 'args', [None])[0]
                    err_text = str(db_error)

                    # If unknown column 'servicios_extra', retry insert without that column
                    if 'Unknown column' in err_text and 'servicios_extra' in err_text:
                        cur.execute(
                            """
                            INSERT INTO arrendatarios_J0 
                            (nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,
                             personas_por_arrendatario, telefono, email, in_house_location)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                arrendatario.nombre_arrendatario,
                                arrendatario.nombre_ubicacion,
                                arrendatario.direccion_ubicacion,
                                arrendatario.personas_por_arrendatario,
                                arrendatario.telefono,
                                arrendatario.email,
                                arrendatario.in_house_location
                            )
                        )
                    elif "Field 'id' doesn't have a default value" in err_text or err_code == 1364:
                        # Fallback for id default missing (error 1364) - manually insert with calculated id
                        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM arrendatarios_J0")
                        next_row = cur.fetchone() or {"next_id": 1}
                        next_id = int(next_row.get("next_id", 1))

                        # Try to insert including servicios_extra if possible
                        try:
                            cur.execute(
                                """
                                INSERT INTO arrendatarios_J0 
                                (id, nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,
                                 personas_por_arrendatario, telefono, email, in_house_location, servicios_extra)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    next_id,
                                    arrendatario.nombre_arrendatario,
                                    arrendatario.nombre_ubicacion,
                                    arrendatario.direccion_ubicacion,
                                    arrendatario.personas_por_arrendatario,
                                    arrendatario.telefono,
                                    arrendatario.email,
                                    arrendatario.in_house_location,
                                    servicios_extra_json
                                )
                            )
                        except Exception:
                            # Last resort: insert without servicios_extra
                            cur.execute(
                                """
                                INSERT INTO arrendatarios_J0 
                                (id, nombre_arrendatario, nombre_ubicacion, direccion_ubicacion,
                                 personas_por_arrendatario, telefono, email, in_house_location)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    next_id,
                                    arrendatario.nombre_arrendatario,
                                    arrendatario.nombre_ubicacion,
                                    arrendatario.direccion_ubicacion,
                                    arrendatario.personas_por_arrendatario,
                                    arrendatario.telefono,
                                    arrendatario.email,
                                    arrendatario.in_house_location
                                )
                            )
                    else:
                        # Unknown error - re-raise
                        raise
                conn.commit()
                new_id = cur.lastrowid or next_id
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
                import json
                servicios_extra_json = None
                if getattr(datos, 'servicios_extra', None) is not None:
                    try:
                        servicios_extra_json = json.dumps([c.dict() if hasattr(c, 'dict') else c for c in datos.servicios_extra])
                    except Exception:
                        servicios_extra_json = None

                try:
                    cur.execute(
                        """
                        UPDATE arrendatarios_J0 
                        SET nombre_arrendatario = %s, nombre_ubicacion = %s, 
                            direccion_ubicacion = %s, personas_por_arrendatario = %s, 
                            telefono = %s, email = %s, in_house_location = %s, servicios_extra = %s
                        WHERE id = %s
                        """,
                        (
                            datos.nombre_arrendatario,
                            datos.nombre_ubicacion,
                            datos.direccion_ubicacion,
                            datos.personas_por_arrendatario,
                            datos.telefono,
                            datos.email,
                            datos.in_house_location,
                            servicios_extra_json,
                            arrendatario_id
                        )
                    )
                except Exception as db_error:
                    # If servicios_extra column doesn't exist, fall back to update without it
                    if 'Unknown column' in str(db_error) and 'servicios_extra' in str(db_error):
                        cur.execute(
                            """
                            UPDATE arrendatarios_J0 
                            SET nombre_arrendatario = %s, nombre_ubicacion = %s, 
                                direccion_ubicacion = %s, personas_por_arrendatario = %s, 
                                telefono = %s, email = %s, in_house_location = %s
                            WHERE id = %s
                            """,
                            (
                                datos.nombre_arrendatario,
                                datos.nombre_ubicacion,
                                datos.direccion_ubicacion,
                                datos.personas_por_arrendatario,
                                datos.telefono,
                                datos.email,
                                datos.in_house_location,
                                arrendatario_id
                            )
                        )
                    else:
                        raise
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

"""Service for managing receipt history and traceability."""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import json

from utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class ReciboService:
    """Service for managing receipt history and storage."""
    
    @staticmethod
    def guardar_historial_recibos(personas_list: List[Dict], mes: int, anio: int) -> bool:
        """
        Save receipt history for multiple tenants in a single transaction.
        
        Args:
            personas_list: List of dicts with: nombre, id_arrendatario, ubicacion, direccion, 
                          personas_por_arrendatario, servicios (dict), servicios_extra (list)
            mes: Month (1-12)
            anio: Year
            
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            conn.begin()  # Explicit transaction start
            
            for persona in personas_list:
                id_recibo = str(uuid.uuid4())
                id_arrendatario = persona.get("id_arrendatario") or persona.get("id") or 0
                nombre_arrendatario = persona.get("nombre", "")
                
                # Calculate total
                servicios = persona.get("servicios", {})
                valor_total = sum(float(v) for v in servicios.values() if v)
                
                # Add servicios_extra if present
                servicios_extra = persona.get("servicios_extra") or []
                for extra in servicios_extra:
                    if isinstance(extra, dict):
                        try:
                            valor_total += float(extra.get("valor", 0) or 0)
                        except (ValueError, TypeError):
                            pass
                
                # Insert into recibos
                insert_recibo = """
                INSERT INTO recibos 
                (id_recibo, id_arrendatario, nombre_arrendatario, mes, anio, valor_total, fecha_generacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                
                cursor.execute(insert_recibo, (
                    id_recibo,
                    id_arrendatario,
                    nombre_arrendatario,
                    mes,
                    anio,
                    valor_total
                ))
                
                # Get the inserted ID
                id_recibo_fk = cursor.lastrowid
                
                # Insert details (servicios principales)
                insert_detalle = """
                INSERT INTO recibo_detalle (id_recibo_fk, concepto, valor)
                VALUES (%s, %s, %s)
                """
                
                for concepto, valor in servicios.items():
                    if valor:
                        try:
                            cursor.execute(insert_detalle, (
                                id_recibo_fk,
                                str(concepto).capitalize(),
                                float(valor)
                            ))
                        except Exception as e:
                            logger.warning(f"Error inserting detail {concepto}: {e}")
                
                # Insert servicios_extra
                for extra in servicios_extra:
                    if isinstance(extra, dict):
                        concepto = extra.get("descripcion", "Concepto adicional")
                        valor = extra.get("valor", 0)
                        if valor:
                            try:
                                cursor.execute(insert_detalle, (
                                    id_recibo_fk,
                                    str(concepto),
                                    float(valor)
                                ))
                            except Exception as e:
                                logger.warning(f"Error inserting extra detail {concepto}: {e}")
            
            conn.commit()
            logger.info(f"Saved {len(personas_list)} receipt records for {mes}/{anio}")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving receipt history: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def listar_recibos(
        mes: Optional[int] = None,
        anio: Optional[int] = None,
        id_arrendatario: Optional[int] = None,
        nombre_arrendatario: Optional[str] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        List receipts with optional filtering.
        
        Args:
            mes: Filter by month (1-12), optional
            anio: Filter by year, optional
            id_arrendatario: Filter by tenant ID, optional
            nombre_arrendatario: Search by tenant name (partial match), optional
            limite: Limit results
            offset: Pagination offset
            
        Returns:
            List of receipt records
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            # Build dynamic query
            query = """
            SELECT 
                id, id_recibo, id_arrendatario, nombre_arrendatario, 
                mes, anio, valor_total, fecha_generacion
            FROM recibos
            WHERE 1=1
            """
            params = []
            
            if mes is not None:
                query += " AND mes = %s"
                params.append(mes)
            
            if anio is not None:
                query += " AND anio = %s"
                params.append(anio)
            
            if id_arrendatario is not None:
                query += " AND id_arrendatario = %s"
                params.append(id_arrendatario)
            
            if nombre_arrendatario:
                query += " AND nombre_arrendatario LIKE %s"
                params.append(f"%{nombre_arrendatario}%")
            
            # Order by most recent first
            query += " ORDER BY fecha_generacion DESC LIMIT %s OFFSET %s"
            params.extend([limite, offset])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return results or []
            
        except Exception as e:
            logger.error(f"Error listing receipts: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def obtener_detalle_recibo(id_recibo: int) -> Dict:
        """
        Get detailed information for a specific receipt.
        
        Args:
            id_recibo: Receipt ID
            
        Returns:
            Dictionary with receipt header and details
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            # Get header
            query_header = """
            SELECT 
                id, id_recibo, id_arrendatario, nombre_arrendatario, 
                mes, anio, valor_total, fecha_generacion
            FROM recibos
            WHERE id = %s
            """
            cursor.execute(query_header, (id_recibo,))
            header = cursor.fetchone()
            
            if not header:
                return {}
            
            # Get details
            query_details = """
            SELECT concepto, valor
            FROM recibo_detalle
            WHERE id_recibo_fk = %s
            ORDER BY concepto
            """
            cursor.execute(query_details, (id_recibo,))
            details = cursor.fetchall()
            
            return {
                **header,
                "detalles": details or []
            }
            
        except Exception as e:
            logger.error(f"Error getting receipt detail: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def obtener_meses_disponibles(anio: Optional[int] = None) -> List[Dict]:
        """
        Get list of available months with receipt data.
        
        Args:
            anio: Optional year filter
            
        Returns:
            List of {mes, anio, cantidad}
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            query = """
            SELECT DISTINCT mes, anio, COUNT(*) as cantidad
            FROM recibos
            """
            params = []
            
            if anio is not None:
                query += " WHERE anio = %s"
                params.append(anio)
            
            query += " GROUP BY mes, anio ORDER BY anio DESC, mes DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return results or []
            
        except Exception as e:
            logger.error(f"Error getting available months: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def obtener_anos_disponibles() -> List[int]:
        """Get list of available years with receipt data."""
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            query = "SELECT DISTINCT anio FROM recibos ORDER BY anio DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [row["anio"] for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Error getting available years: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

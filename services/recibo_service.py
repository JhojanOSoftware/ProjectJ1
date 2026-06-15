"""Service for managing receipt history and database persistence."""
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from utils.database import DatabaseConnection

logger = logging.getLogger(__name__)

class ReciboService:
    """Service for managing receipt history and storage."""
    
    @staticmethod
    def guardar_historial_recibos(recibos_list: List[Dict], mes: str, anio: int) -> bool:
        """
        Save receipt history for multiple tenants in a single transaction.
        
        Args:
            recibos_list: List of dicts with: id_arrendatario, nombre_arrendatario, 
                          monto_total, pdf_base64, detalle (list of {concepto, monto})
            mes: Month name (e.g., 'Junio')
            anio: Year (e.g., 2026)
            
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            conn.begin()  # Start transaction
            
            for recibo in recibos_list:
                id_arrendatario = recibo.get("id_arrendatario")
                nombre_arrendatario = recibo.get("nombre_arrendatario")
                monto_total = recibo.get("monto_total")
                pdf_base64 = recibo.get("pdf_base64")
                
                # Insert into recibos
                insert_recibo = """
                INSERT INTO recibos 
                (id_arrendatario, nombre_arrendatario, mes, anio, monto_total, pdf_base64, fecha_generacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                cursor.execute(insert_recibo, (
                    id_arrendatario,
                    nombre_arrendatario,
                    mes,
                    anio,
                    monto_total,
                    pdf_base64
                ))
                
                # Get the inserted id_recibo
                id_recibo = cursor.lastrowid
                
                # Insert details into recibo_detalle
                insert_detalle = """
                INSERT INTO recibo_detalle (id_recibo, concepto, monto)
                VALUES (%s, %s, %s)
                """
                
                for det in recibo.get("detalle", []):
                    cursor.execute(insert_detalle, (
                        id_recibo,
                        det.get("concepto"),
                        det.get("monto")
                    ))
            
            conn.commit()
            logger.info(f"Saved {len(recibos_list)} receipt records for {mes}/{anio}")
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
        mes: Optional[str] = None,
        anio: Optional[int] = None,
        id_arrendatario: Optional[int] = None
    ) -> List[Dict]:
        """
        List receipts with optional filtering.
        
        Args:
            mes: Filter by month name, optional
            anio: Filter by year, optional
            id_arrendatario: Filter by tenant ID, optional
            
        Returns:
            List of receipt records with details (excluding pdf_base64)
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            query = """
            SELECT 
                id_recibo, id_arrendatario, nombre_arrendatario, 
                mes, anio, monto_total, fecha_generacion
            FROM recibos
            WHERE 1=1
            """
            params = []
            
            if mes:
                query += " AND mes = %s"
                params.append(mes)
            
            if anio is not None:
                query += " AND anio = %s"
                params.append(anio)
            
            if id_arrendatario is not None:
                query += " AND id_arrendatario = %s"
                params.append(id_arrendatario)
            
            query += " ORDER BY fecha_generacion DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            recibos = []
            for row in results:
                # Convert datetime to string
                fecha = row["fecha_generacion"]
                if isinstance(fecha, datetime):
                    fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    fecha_str = str(fecha)
                
                # Fetch details
                cursor.execute(
                    "SELECT concepto, monto FROM recibo_detalle WHERE id_recibo = %s",
                    (row["id_recibo"],)
                )
                details = cursor.fetchall()
                
                recibos.append({
                    "id_recibo": row["id_recibo"],
                    "id_arrendatario": row["id_arrendatario"],
                    "nombre_arrendatario": row["nombre_arrendatario"],
                    "mes": row["mes"],
                    "anio": row["anio"],
                    "monto_total": float(row["monto_total"]),
                    "fecha_generacion": fecha_str,
                    "detalle": [{"concepto": d["concepto"], "monto": float(d["monto"])} for d in details]
                })
                
            return recibos
            
        except Exception as e:
            logger.error(f"Error listing receipts: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def obtener_pdf_recibo(id_recibo: int) -> Optional[Tuple[str, str]]:
        """
        Get PDF base64 for a specific receipt.
        
        Args:
            id_recibo: Receipt ID
            
        Returns:
            Tuple of (nombre_arrendatario, pdf_base64) or None
        """
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT nombre_arrendatario, pdf_base64 FROM recibos WHERE id_recibo = %s",
                (id_recibo,)
            )
            row = cursor.fetchone()
            if row:
                return row["nombre_arrendatario"], row["pdf_base64"]
            return None
        except Exception as e:
            logger.error(f"Error getting pdf for receipt {id_recibo}: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

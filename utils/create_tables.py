"""Script to create recibos and recibo_detalle tables in MySQL."""
import logging
import pymysql
from dotenv import load_dotenv
load_dotenv()
from utils.database import DatabaseConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()
    
    try:
        logger.info("Creating recibos table...")
        create_recibos = """
        CREATE TABLE IF NOT EXISTS recibos (
          id_recibo INT AUTO_INCREMENT PRIMARY KEY,
          id_arrendatario BIGINT NOT NULL,
          nombre_arrendatario VARCHAR(255) NOT NULL,
          mes VARCHAR(20) NOT NULL,
          anio INT NOT NULL,
          monto_total DECIMAL(10,2) NOT NULL,
          pdf_base64 LONGTEXT,
          fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (id_arrendatario) REFERENCES arrendatarios_J0(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_recibos)
        
        logger.info("Creating recibo_detalle table...")
        create_detalle = """
        CREATE TABLE IF NOT EXISTS recibo_detalle (
          id_detalle INT AUTO_INCREMENT PRIMARY KEY,
          id_recibo INT NOT NULL,
          concepto VARCHAR(100) NOT NULL,
          monto DECIMAL(10,2) NOT NULL,
          FOREIGN KEY (id_recibo) REFERENCES recibos(id_recibo) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_detalle)
        
        logger.info("Creating indexes...")
        try:
            cursor.execute("CREATE INDEX idx_recibos_mes_anio ON recibos(mes, anio)")
        except Exception as e:
            logger.info(f"Index idx_recibos_mes_anio might already exist: {e}")
            
        try:
            cursor.execute("CREATE INDEX idx_recibos_arrendatario ON recibos(id_arrendatario)")
        except Exception as e:
            logger.info(f"Index idx_recibos_arrendatario might already exist: {e}")
            
        conn.commit()
        logger.info("Tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()

"""Service for PDF generation and management."""
import logging
import os
import tempfile
import zipfile
import shutil
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Import receipt generation from recexamples
try:
    from recexamples import GenerarComprobantes
    PDF_GENERATION_AVAILABLE = True
except ImportError:
    PDF_GENERATION_AVAILABLE = False
    logger.warning("PDF generation module not available")


class PDFService:
    """Service for managing PDF generation and file operations."""
    
    @staticmethod
    def generar_comprobantes_zip(
        servicios_dict: Dict,
        nombre_arrendatario: str,
        nombre_ubicacion: str,
        direccion_ubicacion: str,
        personas_por_arrendatario: int,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a single PDF receipt.
        
        Args:
            servicios_dict: Dictionary of services and their values
            nombre_arrendatario: Tenant name
            nombre_ubicacion: Location name
            direccion_ubicacion: Location address
            personas_por_arrendatario: Number of people in unit
            output_path: Optional custom output path
            
        Returns:
            Path to generated PDF or None if error
        """
        if not PDF_GENERATION_AVAILABLE:
            logger.error("PDF generation not available")
            raise ImportError("PDF generation module required")
        
        try:
            pdf_path = GenerarComprobantes(
                servicios_dict=servicios_dict,
                nombre_arrendatario=nombre_arrendatario,
                nombre_ubicacion=nombre_ubicacion,
                direccion_ubicacion=direccion_ubicacion,
                personas_por_arrendatario=personas_por_arrendatario,
                output_path=output_path
            )
            
            if pdf_path and os.path.exists(pdf_path):
                logger.info(f"Generated PDF: {pdf_path}")
                return pdf_path
            else:
                logger.error(f"PDF generation failed for {nombre_arrendatario}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating PDF for {nombre_arrendatario}: {e}")
            raise
    
    @staticmethod
    def generar_multiples_pdfs(personas_list: List[Dict]) -> tuple[str, List[str]]:
        """
        Generate multiple PDFs and package them in a ZIP file.
        
        Args:
            personas_list: List of person dictionaries with service info
            
        Returns:
            Tuple of (zip_path, list_of_pdfs)
        """
        temp_dir = tempfile.mkdtemp(prefix="comprobantes_")
        archivos = []
        
        try:
            for persona in personas_list:
                servicios = persona.get("servicios", {})
                
                # Convert to dictionary format if needed
                if not isinstance(servicios, dict):
                    servicios_dict = {
                        'agua': servicios.get('agua', 0),
                        'luz': servicios.get('luz', 0),
                        'aseo': servicios.get('aseo', 0),
                        'gas': servicios.get('gas', 0)
                    }
                else:
                    servicios_dict = servicios
                
                pdf_path = PDFService.generar_comprobantes_zip(
                    servicios_dict=servicios_dict,
                    nombre_arrendatario=persona['nombre'],
                    nombre_ubicacion=persona['ubicacion'],
                    direccion_ubicacion=persona['direccion'],
                    personas_por_arrendatario=persona.get('personas_por_arrendatario', 1),
                    output_path=temp_dir
                )
                
                if pdf_path and os.path.exists(pdf_path):
                    archivos.append(pdf_path)
                else:
                    logger.warning(f"Failed to generate PDF for {persona['nombre']}")
            
            # Create ZIP file
            zip_filename = f'comprobantes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file_path in archivos:
                    zipf.write(file_path, arcname=os.path.basename(file_path))
            
            logger.info(f"Created ZIP with {len(archivos)} PDFs: {zip_path}")
            return zip_path, archivos
            
        except Exception as e:
            logger.error(f"Error generating multiple PDFs: {e}")
            # Clean up on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise
    
    @staticmethod
    def cleanup_temp_files(paths: List[str]) -> None:
        """
        Clean up temporary files and directories.
        
        Args:
            paths: List of file or directory paths to remove
        """
        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logger.debug(f"Removed file: {path}")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    logger.debug(f"Removed directory: {path}")
            except Exception as e:
                logger.warning(f"Error removing {path}: {e}")

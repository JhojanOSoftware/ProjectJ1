"""Business logic for service calculations (utilities: water, light, gas, cleaning)."""
import logging
from typing import Dict, Tuple, List
from services.arrendatario_service import ArrendatarioService

logger = logging.getLogger(__name__)


class ServiciosService:
    """Service for calculating utility charges for arrendatarios."""
    
    @staticmethod
    def calcular_servicios(
        water_value: float,
        luz_value: float,
        aseo_value: float,
        gas_value: float,
        personas_por_arrendatario: int,
        nombre_ubicacion: str,
        cantidad_arrendatarios: int
    ) -> Tuple[float, float, float, float]:
        """
        Calculate service charges for a specific arrendatario.
        
        Args:
            water_value: Total monthly water cost
            luz_value: Total monthly electricity cost
            aseo_value: Total monthly cleaning cost
            gas_value: Total monthly gas cost
            personas_por_arrendatario: Number of people in this unit
            nombre_ubicacion: Location name
            cantidad_arrendatarios: Total number of units in location
            
        Returns:
            Tuple of (water_price, luz_price, aseo_price, gas_price)
        """
        try:
            # Water is split by number of people
            headcount = max(1, ArrendatarioService.get_total_personas(nombre_ubicacion))
            valor_unitario_agua = water_value / headcount
            precio_agua = valor_unitario_agua * personas_por_arrendatario
            
            # Other services split equally by number of units
            div = max(1, cantidad_arrendatarios)
            precio_luz = luz_value / div
            precio_aseo = aseo_value / div
            precio_gas = gas_value / div
            
            logger.debug(
                f"Calculated services for {nombre_ubicacion}: "
                f"Agua={precio_agua:.2f}, Luz={precio_luz:.2f}, "
                f"Aseo={precio_aseo:.2f}, Gas={precio_gas:.2f}"
            )
            
            return (precio_agua, precio_luz, precio_aseo, precio_gas)
        except Exception as e:
            logger.error(f"Error calculating services: {e}")
            raise
    
    @staticmethod
    def build_preview(
        water_value: float,
        luz_value: float,
        aseo_value: float,
        gas_value: float,
        nombre_ubicacion: str
    ) -> Dict:
        """
        Build a preview of all service charges for a location.
        
        Returns a dictionary with detailed breakdown for each arrendatario.
        """
        try:
            arrendatarios = ArrendatarioService.get_arrendatarios_by_location(nombre_ubicacion)
            cantidad_arrendatarios = len(arrendatarios)
            
            preview_items = []
            suma_total = 0
            
            for arr in arrendatarios:
                arrendatario_id = arr["id"]
                nombre_arrendatario = arr["nombre_arrendatario"]
                direccion_ubicacion = arr["direccion_ubicacion"]
                personas_por_arrendatario = int(arr.get("personas_por_arrendatario") or 1)
                
                precio_agua, precio_luz, precio_aseo, precio_gas = ServiciosService.calcular_servicios(
                    water_value, luz_value, aseo_value, gas_value,
                    personas_por_arrendatario, nombre_ubicacion, cantidad_arrendatarios
                )
                
                total = precio_agua + precio_luz + precio_aseo + precio_gas

                # include any servicios_extra that may be present in the arr record
                extras_total = 0
                extras = []
                if 'servicios_extra' in arr and arr.get('servicios_extra'):
                    try:
                        # arr['servicios_extra'] may be list or JSON string
                        import json
                        se = arr.get('servicios_extra')
                        if isinstance(se, str):
                            se_list = json.loads(se)
                        else:
                            se_list = se
                        for item in se_list or []:
                            # item may be dict with descripcion/valor
                            valor = item.get('valor') if isinstance(item, dict) else None
                            try:
                                vnum = float(valor)
                            except Exception:
                                vnum = 0
                            extras_total += vnum
                            extras.append({
                                'descripcion': item.get('descripcion') if isinstance(item, dict) else str(item),
                                'valor': vnum
                            })
                    except Exception:
                        extras = []

                total += extras_total
                suma_total += total
                
                preview_items.append({
                    "id": arrendatario_id,
                    "nombre_arrendatario": nombre_arrendatario,
                    "nombre_ubicacion": nombre_ubicacion,
                    "direccion_ubicacion": direccion_ubicacion,
                    "personas_por_arrendatario": personas_por_arrendatario,
                    "servicios": {
                        "agua": round(precio_agua, 2),
                        "luz": round(precio_luz, 2),
                        "aseo": round(precio_aseo, 2),
                        "gas": round(precio_gas, 2)
                    },
                    "total": round(total, 2),
                    "servicios_extra": extras
                })
            
            logger.info(f"Preview built for {nombre_ubicacion}: {cantidad_arrendatarios} units")
            
            return {
                "ubicacion": nombre_ubicacion,
                "arrendatarios": preview_items,
                "sum_total": round(suma_total, 2)
            }
        except Exception as e:
            logger.error(f"Error building preview: {e}")
            raise

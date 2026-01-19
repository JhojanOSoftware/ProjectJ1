from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, validator

class ArrendatarioUpdate(BaseModel):
    nombre_arrendatario: str
    nombre_ubicacion: str 
    direccion_ubicacion: str
    personas_por_arrendatario: int 
    telefono: Optional[str] = None
    email: Optional[str] = None


class Arrendatario(BaseModel):
    id: Optional[int] = Field(None, description="ID del arrendatario (autogenerado)")
    nombre_arrendatario: Annotated[str, Field(..., min_length=1, max_length=500, description="Nombre del arrendatario")]
    nombre_ubicacion: Annotated[str, Field(..., min_length=1, max_length=500, description="Ubicación del arrendatario")]
    direccion_ubicacion: Annotated[str, Field(..., min_length=1, max_length=500, description="Dirección del arrendatario")]
    personas_por_arrendatario: Annotated[int, Field(..., gt=0, lt=100, description="Número de personas por arrendatario")]
    telefono: Annotated[str, Field(..., min_length=5, max_length=30, description="Número de teléfono del arrendatario")]
    email: Annotated[str, Field(..., min_length=5, max_length=320, description="Correo electrónico del arrendatario")]

class Concepto(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=200,         description="Descripción del concepto (Luz, Agua, Gas, etc.)")
    valor: float = Field(..., gt=0, description="Valor del concepto")

class PersonaEditada(BaseModel):
    id: int = Field(..., gt=0, description="ID del arrendatario")
    nombre: str = Field(..., min_length=1, max_length=100)
    ubicacion: str = Field(..., min_length=1, max_length=100)
    direccion: str = Field(..., min_length=1, max_length=200)
    personas_por_arrendatario: Optional[int] = Field(None, gt=0)
    servicios: List[Concepto] = Field(default_factory=list)

class PDFData(BaseModel):
    personas: List[PersonaEditada] = Field(..., min_items=1)


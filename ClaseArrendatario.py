from typing import Optional, Annotated
from pydantic import BaseModel, Field, validator


class Arrendatario(BaseModel):
    id: Optional[int] = Field(None, description="ID del arrendatario (autogenerado)")
    nombre_arrendatario: Annotated[str, Field(..., min_length=1, max_length=500, description="Nombre del arrendatario")]
    nombre_ubicacion: Annotated[str, Field(..., min_length=1, max_length=500, description="Ubicación del arrendatario")]
    direccion_ubicacion: Annotated[str, Field(..., min_length=1, max_length=500, description="Dirección del arrendatario")]
    telefono: Annotated[str, Field(..., min_length=5, max_length=30, description="Número de teléfono del arrendatario")]
    email: Annotated[str, Field(..., min_length=5, max_length=320, description="Correo electrónico del arrendatario")]





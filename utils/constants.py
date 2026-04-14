"""Application constants and enumerations."""
from enum import Enum
from typing import List


class ServiceType(str, Enum):
    """Service types for utility calculations."""
    AGUA = "agua"
    LUZ = "luz"
    ASEO = "aseo"
    GAS = "gas"


SERVICE_NAMES = {
    ServiceType.AGUA: "Agua",
    ServiceType.LUZ: "Luz",
    ServiceType.ASEO: "Aseo",
    ServiceType.GAS: "Gas"
}

ALL_SERVICES: List[ServiceType] = [
    ServiceType.AGUA,
    ServiceType.LUZ,
    ServiceType.ASEO,
    ServiceType.GAS
]


class HTTP_STATUS:
    """HTTP status codes for responses."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

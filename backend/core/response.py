"""
Estructura unificada de respuestas API para todos los microservicios.
"""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operación realizada con éxito."
    data: Optional[T] = None
    error: Optional[Any] = None

    @classmethod
    def success_response(cls, data: Optional[T] = None, message: str = "Operación exitosa") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data, error=None)

    @classmethod
    def error_response(cls, message: str, error: Optional[Any] = None) -> "ApiResponse[None]":
        return cls(success=False, message=message, data=None, error=error)

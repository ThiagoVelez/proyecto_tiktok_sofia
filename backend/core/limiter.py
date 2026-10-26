"""
Configuración del Limitador de Tasa (Rate Limiting) con SlowAPI.
Protege contra ataques de denegación de servicio (DoS) y fuerza bruta en autenticación.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .response import ApiResponse


def _get_key_func(request: Request) -> str:
    """Extrae la clave para limitar la tasa: IP remota o identificador de usuario."""
    # Soporte para proxies inversos (X-Forwarded-For)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request) or "127.0.0.1"


# Inicializar el limitador SlowAPI
limiter = Limiter(
    key_func=_get_key_func,
    default_limits=["120/minute"] if settings.RATE_LIMIT_ENABLED else ["10000/minute"],
    enabled=settings.RATE_LIMIT_ENABLED
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Manejador estandarizado cuando un cliente supera la cuota de peticiones permitidas."""
    return JSONResponse(
        status_code=429,
        content=ApiResponse.error_response(
            message=f"Demasiadas solicitudes. Límite excedido: {exc.detail}. Intenta de nuevo más tarde.",
            error={"type": "RATE_LIMIT_EXCEEDED", "detail": str(exc.detail)}
        ).model_dump(),
        headers={"Retry-After": "60"}
    )

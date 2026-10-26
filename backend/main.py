"""
================================================================================
PROYECTO SOFÍA - BACKEND TIKTOK-LIKE API GATEWAY & MICROSERVICES ORCHESTRATOR
================================================================================
Arquitectura: Modular, SOLID y orientada a microservicios distribuidos.
Incluye motor de reglas de negocio en `reglas/` para control parental y seguridad
de contenido para proteger a toda la audiencia.
Hardening: Cabeceras de seguridad, limitador de tasa (Rate Limiting), WebSocket
en tiempo real, observabilidad estructurada y monitoreo profundo de salud.
================================================================================
"""

import os
import time
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded

from backend.core.config import settings
from backend.core.exceptions import SofiaBaseException, ParentalRestrictionException, ContentSafetyException
from backend.core.response import ApiResponse
from backend.core.limiter import limiter, rate_limit_exceeded_handler
from backend.core.logging import logger, correlation_id_ctx
from backend.core.database import get_db
from backend.core.redis_client import redis_manager
from backend.core.websockets import ws_router

# Importación de Routers de cada Microservicio Desacoplado
from backend.microservices.auth_service import auth_router
from backend.microservices.user_service import user_router
from backend.microservices.video_service import video_router
from backend.microservices.interaction_service import interaction_router
from backend.microservices.moderation_service import moderation_router
from backend.microservices.notification_service import notification_router
from backend.microservices.search_service import search_router
from backend.microservices.story_service import story_router

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="Proyecto Sofía API - Plataforma de Videos Cortos (TikTok)",
    description=(
        "Backend modular y distribuido en microservicios. Cuenta con motor de reglas "
        "de negocio en tiempo real para Control Parental, Protección de Audiencia infantil/adolescente, "
        "y moderación de contenidos."
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Integración del Limitador de Tasa
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# ==============================================================================
# MIDDLEWARES DE SEGURIDAD Y TRAZABILIDAD
# ==============================================================================

@app.middleware("http")
async def security_and_tracing_middleware(request: Request, call_next):
    """
    Inyecta ID de correlación único y aplica cabeceras de seguridad HTTP
    (OWASP Security Headers / HSTS / Clickjacking / Sniffing protection).
    """
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    correlation_id_ctx.set(request_id)
    start_time = time.time()

    response: Response = await call_next(request)

    process_time_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time_ms}ms"

    if settings.SECURITY_HEADERS_ENABLED:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# Configuración estricta de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Content-Range", "Accept-Ranges"]
)

# Garantizar directorios de almacenamiento local para videos, miniaturas, historias y avatares
os.makedirs(os.path.join(settings.UPLOAD_DIR, "videos"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "thumbnails"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "stories"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ==============================================================================
# MANEJADORES DE EXCEPCIONES GLOBALES
# ==============================================================================

@app.exception_handler(ParentalRestrictionException)
async def parental_restriction_handler(request: Request, exc: ParentalRestrictionException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ApiResponse.error_response(
            message=exc.detail,
            error={"type": "PARENTAL_CONTROL_RESTRICTION", "code": exc.error_code}
        ).model_dump()
    )


@app.exception_handler(ContentSafetyException)
async def content_safety_handler(request: Request, exc: ContentSafetyException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse.error_response(
            message=exc.detail,
            error={"type": "CONTENT_SAFETY_VIOLATION", "violations": exc.violations}
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejo controlado de errores de validación de esquemas sin filtrar internas."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({"field": loc, "message": err.get("msg")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse.error_response(
            message="Error de validación en los datos enviados.",
            error={"type": "VALIDATION_ERROR", "details": errors}
        ).model_dump()
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Protección contra fuga de información de la base de datos en errores SQL."""
    logger.error(f"Error de base de datos no capturado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error_response(
            message="Ocurrió un error en la base de datos. La operación fue abortada.",
            error={"type": "DATABASE_ERROR"}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador final para prevenir fugas de stack trace al usuario."""
    logger.error(f"Excepción interna no controlada: {exc}", exc_info=True)
    msg = str(exc) if settings.DEBUG else "Error interno del servidor."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error_response(
            message=msg,
            error={"type": "INTERNAL_SERVER_ERROR"}
        ).model_dump()
    )


# ==============================================================================
# REGISTRO DE MICROSERVICIOS Y WEBSOCKETS (API GATEWAY / ROUTING)
# ==============================================================================

API_V1_PREFIX = "/api/v1"

app.include_router(ws_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(user_router, prefix=API_V1_PREFIX)
app.include_router(video_router, prefix=API_V1_PREFIX)
app.include_router(story_router, prefix=API_V1_PREFIX)
app.include_router(interaction_router, prefix=API_V1_PREFIX)
app.include_router(moderation_router, prefix=API_V1_PREFIX)
app.include_router(notification_router, prefix=API_V1_PREFIX)
app.include_router(search_router, prefix=API_V1_PREFIX)


# ==============================================================================
# ENDPOINTS DE SALUD, MÉTRICAS Y RAÍZ
# ==============================================================================

@app.get("/", tags=["Sistema"])
def root_info():
    """Información general de la arquitectura y servicios en ejecución."""
    return ApiResponse.success_response(
        data={
            "platform": "Proyecto Sofía",
            "architecture": "Modular Microservices (SOLID)",
            "rules_engine": "backend/reglas (Active)",
            "storage_backend": settings.STORAGE_BACKEND,
            "security_headers": settings.SECURITY_HEADERS_ENABLED,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "websockets": "Active (/api/v1/ws)",
            "docs": "/docs",
            "version": "1.1.0"
        },
        message="Backend de Proyecto Sofía operando con éxito."
    )


@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    """
    Monitoreo profundo de salud y disponibilidad.
    Verifica activamente conectividad con Base de Datos, Redis y Almacenamiento.
    """
    components = {}

    # 1. Comprobar Base de Datos
    try:
        db.execute(text("SELECT 1"))
        components["database"] = {"status": "up", "driver": "pymysql/sqlite"}
    except Exception as e:
        components["database"] = {"status": "down", "error": str(e)}

    # 2. Comprobar Redis
    redis_healthy = redis_manager.ping()
    components["redis"] = {
        "status": "up" if redis_healthy else "fallback_or_unreachable",
        "mode": "redis" if redis_healthy else "in_memory_fallback"
    }

    # 3. Comprobar Almacenamiento
    components["storage"] = {
        "status": "up",
        "backend": settings.STORAGE_BACKEND,
        "max_size_mb": settings.MAX_VIDEO_SIZE_MB
    }

    is_overall_healthy = components["database"]["status"] == "up"

    return ApiResponse.success_response(
        data={
            "status": "healthy" if is_overall_healthy else "degraded",
            "service": "api-gateway",
            "components": components
        },
        message="Servicios operativos correctamente." if is_overall_healthy else "Estado degradado."
    )


@app.get("/metrics", tags=["Sistema"])
def prometheus_metrics():
    """Endpoint básico para telemetría y scraping de métricas Prometheus."""
    metrics = [
        "# HELP sofia_app_info Metadatos de la aplicación",
        "# TYPE sofia_app_info gauge",
        'sofia_app_info{version="1.1.0",env="production"} 1',
        "# HELP sofia_health_status Estado de salud del sistema",
        "# TYPE sofia_health_status gauge",
        "sofia_health_status 1"
    ]
    return PlainTextResponse("\n".join(metrics) + "\n", media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

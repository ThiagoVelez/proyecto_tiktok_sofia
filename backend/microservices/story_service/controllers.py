"""
Controladores / Endpoints REST del Microservicio de Historias (Stories)
Permite subir historias de foto o video con expiración a las 24 horas, visualizar feed y métricas.
"""

import re
from pathlib import Path
from uuid import uuid4
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, get_current_user_optional
from backend.core.response import ApiResponse
from backend.core.limiter import limiter
from backend.core.storage import validate_file_magic_bytes
from .schemas import (
    StoryCreateRequest, StoryDetail, StoryFeedResponse,
    StoryViewersResponse
)
from .service import StoryService

router = APIRouter(prefix="/stories", tags=["Historias (Stories 24h)"])


@router.post("/publish", response_model=ApiResponse[StoryDetail], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_UPLOAD_PER_MINUTE)
async def publish_story_file(
    request: Request,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    media_type: str = Form("auto", description="'video', 'image' o 'auto'"),
    duration_seconds: float = Form(5.0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube y publica directamente un archivo de historia (video o imagen) en una sola petición.
    Expira de forma automática a las 24 horas y evalúa reglas de moderación.
    """
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    all_allowed = settings.ALLOWED_VIDEO_EXTENSIONS + settings.ALLOWED_IMAGE_EXTENSIONS

    if ext not in all_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido para historias. Permitidos: {', '.join(all_allowed)}"
        )

    # Detección de tipo de medio si es 'auto'
    if media_type == "auto":
        detected_type = "video" if ext in settings.ALLOWED_VIDEO_EXTENSIONS else "image"
    else:
        detected_type = media_type

    first_chunk = await file.read(1024)
    if not first_chunk:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo de historia está vacío.")

    media_category = "video" if detected_type == "video" else "image"
    if not validate_file_magic_bytes(first_chunk, media_category):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firma binaria del archivo no válida o contenido corrupto."
        )

    stories_dir = Path(settings.UPLOAD_DIR) / "stories"
    stories_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"story_{uuid4().hex[:12]}_{re.sub(r'[^a-zA-Z0-9_.-]', '', file.filename)}"
    destination_path = stories_dir / safe_name

    max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    total_bytes = len(first_chunk)

    with open(destination_path, "wb") as buffer:
        buffer.write(first_chunk)
        while chunk := await file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > max_size_bytes:
                buffer.close()
                destination_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El archivo excede el tamaño máximo permitido ({settings.MAX_VIDEO_SIZE_MB}MB)."
                )
            buffer.write(chunk)

    rel_url = f"/uploads/stories/{safe_name}"

    service = StoryService(db)
    story = service.create_story(
        author=current_user,
        media_url=rel_url,
        media_type=detected_type,
        caption=caption,
        duration_seconds=duration_seconds
    )

    return ApiResponse.success_response(
        data=story,
        message="Historia publicada con éxito. Expira automáticamente en 24 horas."
    )


@router.post("/", response_model=ApiResponse[StoryDetail], status_code=status.HTTP_201_CREATED)
def create_story_json(
    req: StoryCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publica una historia mediante URL de medio ya cargado previamente.
    """
    service = StoryService(db)
    story = service.create_story(
        author=current_user,
        media_url=req.media_url,
        media_type=req.media_type,
        caption=req.caption,
        duration_seconds=req.duration_seconds or 5.0
    )
    return ApiResponse.success_response(
        data=story,
        message="Historia creada con éxito. Expira automáticamente en 24 horas."
    )


@router.get("/feed", response_model=ApiResponse[StoryFeedResponse])
def get_stories_feed(
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Retorna la bandeja superior de historias activas agrupadas por usuario (Estilo Instagram/TikTok).
    Muestra avatares, conteo de historias y si el usuario actual tiene historias pendientes por ver.
    """
    service = StoryService(db)
    feed = service.get_active_feed(viewer=viewer)
    return ApiResponse.success_response(data=feed, message="Bandeja de historias activas obtenida.")


@router.get("/user/{user_id}", response_model=ApiResponse[List[StoryDetail]])
def get_user_stories(
    user_id: int,
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Obtiene todas las historias activas (no expiradas) de un usuario específico."""
    service = StoryService(db)
    stories = service.get_user_stories(user_id=user_id, viewer=viewer)
    return ApiResponse.success_response(data=stories, message="Historias del usuario obtenidas.")


@router.get("/{story_id}", response_model=ApiResponse[StoryDetail])
def get_story_by_id(
    story_id: int,
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Consulta los detalles de una historia específica."""
    service = StoryService(db)
    story = service.get_story_by_id(story_id=story_id, viewer=viewer)
    return ApiResponse.success_response(data=story, message="Historia obtenida.")


@router.post("/{story_id}/view", response_model=ApiResponse[dict])
def register_story_view(
    story_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra la visualización de una historia y actualiza el contador único de vistas."""
    service = StoryService(db)
    result = service.register_story_view(story_id=story_id, viewer=current_user)
    return ApiResponse.success_response(data=result, message="Visualización de historia registrada.")


@router.get("/{story_id}/viewers", response_model=ApiResponse[StoryViewersResponse])
def get_story_viewers(
    story_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Consulta la lista de personas que han visto la historia (solo creador o moderadores)."""
    service = StoryService(db)
    viewers = service.get_story_viewers(story_id=story_id, current_user=current_user)
    return ApiResponse.success_response(data=viewers, message="Lista de espectadores obtenida.")


@router.delete("/{story_id}", response_model=ApiResponse[dict])
def delete_story(
    story_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una historia antes de sus 24 horas (solo creador o moderadores)."""
    service = StoryService(db)
    result = service.delete_story(story_id=story_id, current_user=current_user)
    return ApiResponse.success_response(data=result, message="Historia eliminada exitosamente.")

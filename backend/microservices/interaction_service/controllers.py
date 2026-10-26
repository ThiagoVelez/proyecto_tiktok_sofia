from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, get_current_user_optional
from backend.core.response import ApiResponse
from .schemas import (
    CommentCreateRequest, CommentResponse, LikeToggleResponse,
    BookmarkToggleResponse, ShareRecordRequest, ShareResponse,
    CommentLikeToggleResponse
)
from .service import InteractionService

router = APIRouter(prefix="/interactions", tags=["Interacciones (Likes, Comentarios, Guardados, Compartir)"])


@router.post("/videos/{video_id}/like", response_model=ApiResponse[LikeToggleResponse])
def toggle_video_like(
    video_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Da o quita 'Me Gusta' a un video y genera notificación automática al creador."""
    service = InteractionService(db)
    res = service.toggle_like(current_user, video_id)
    msg = "Like agregado." if res.is_liked else "Like removido."
    return ApiResponse.success_response(data=res, message=msg)


@router.post("/comments/{comment_id}/like", response_model=ApiResponse[CommentLikeToggleResponse])
def toggle_comment_like(
    comment_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Da o quita 'Me Gusta' a un comentario."""
    service = InteractionService(db)
    res = service.toggle_comment_like(current_user, comment_id)
    msg = "Like en comentario agregado." if res.is_liked else "Like en comentario removido."
    return ApiResponse.success_response(data=res, message=msg)


@router.post("/videos/{video_id}/comments", response_model=ApiResponse[CommentResponse], status_code=status.HTTP_201_CREATED)
def post_comment(
    video_id: int,
    req: CommentCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publica un comentario en el video.
    Aplica filtros de seguridad contra ciberacoso, odio y modera lenguaje no apto para menores.
    Notifica automáticamente al creador del video.
    """
    service = InteractionService(db)
    new_comment = service.add_comment(current_user, video_id, req)
    return ApiResponse.success_response(data=new_comment, message="Comentario publicado.")


@router.get("/videos/{video_id}/comments", response_model=ApiResponse[List[CommentResponse]])
def list_comments(
    video_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Lista los comentarios aprobados de un video, indicando si el espectador les dio like."""
    service = InteractionService(db)
    viewer_id = viewer.id if viewer else None
    comments = service.get_video_comments(video_id, viewer_id=viewer_id, limit=limit, offset=offset)
    return ApiResponse.success_response(data=comments, message="Comentarios obtenidos.")


@router.delete("/comments/{comment_id}", response_model=ApiResponse[dict])
def delete_comment(
    comment_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina un comentario existente."""
    service = InteractionService(db)
    service.delete_comment(current_user, comment_id)
    return ApiResponse.success_response(data={"comment_id": comment_id}, message="Comentario eliminado.")


@router.post("/videos/{video_id}/bookmark", response_model=ApiResponse[BookmarkToggleResponse])
def toggle_bookmark(
    video_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Guarda o quita un video de Favoritos/Guardados."""
    service = InteractionService(db)
    res = service.toggle_bookmark(current_user, video_id)
    msg = "Video guardado en Favoritos." if res.is_saved else "Video removido de Favoritos."
    return ApiResponse.success_response(data=res, message=msg)


@router.post("/videos/{video_id}/share", response_model=ApiResponse[ShareResponse])
def record_video_share(
    video_id: int,
    req: ShareRecordRequest,
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Registra que un video fue compartido (WhatsApp, Facebook, Instagram, Twitter, Copiar Enlace, etc.).
    Actualiza la tabla video_shares y retorna enlace listo para compartir en el frontend.
    """
    service = InteractionService(db)
    res = service.record_share(video_id=video_id, platform=req.platform, user=viewer)
    return ApiResponse.success_response(data=res, message="Compartido registrado con éxito.")


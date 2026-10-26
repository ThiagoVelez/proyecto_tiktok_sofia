from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user
from backend.core.response import ApiResponse
from .schemas import NotificationItem, ParentalAlertRequest
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notificaciones y Alertas"])


@router.get("", response_model=ApiResponse[List[NotificationItem]])
def get_user_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Consulta la lista de notificaciones e interacciones recibidas."""
    service = NotificationService(db)
    items = service.get_notifications(current_user.id, unread_only=unread_only, limit=limit, offset=offset)
    return ApiResponse.success_response(data=items, message="Notificaciones obtenidas.")


@router.post("/{notification_id}/read", response_model=ApiResponse[dict])
def mark_notification_as_read(
    notification_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una notificación como leída."""
    service = NotificationService(db)
    service.mark_as_read(current_user.id, notification_id)
    return ApiResponse.success_response(data={"id": notification_id}, message="Notificación marcada como leída.")


@router.post("/parental-alert", response_model=ApiResponse[dict])
def trigger_parental_alert(
    req: ParentalAlertRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Envía una alerta parental al tutor/padre de familia."""
    service = NotificationService(db)
    service.send_parental_alert(current_user.id, req)
    return ApiResponse.success_response(data={}, message="Alerta parental emitida.")

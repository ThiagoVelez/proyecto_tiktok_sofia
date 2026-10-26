from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.core.database import NotificationModel, UserModel
from .schemas import NotificationItem, ParentalAlertRequest


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0) -> List[NotificationItem]:
        query = self.db.query(NotificationModel).filter(NotificationModel.user_id == user_id)
        if unread_only:
            query = query.filter(NotificationModel.is_read == False)

        items = query.order_by(desc(NotificationModel.created_at)).offset(offset).limit(limit).all()

        return [
            NotificationItem(
                id=n.id,
                user_id=n.user_id,
                sender_id=n.sender_id,
                type=n.type,
                title=n.title,
                message=n.message,
                resource_type=n.resource_type,
                resource_id=n.resource_id,
                is_read=n.is_read,
                created_at=n.created_at
            ) for n in items
        ]

    def mark_as_read(self, user_id: int, notification_id: int):
        notif = self.db.query(NotificationModel).filter(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == user_id
        ).first()

        if notif:
            notif.is_read = True
            self.db.commit()

    def send_parental_alert(self, parent_user_id: int, req: ParentalAlertRequest):
        child = self.db.query(UserModel).filter(UserModel.id == req.child_user_id).first()
        child_name = f"@{child.username}" if child else "tu hijo/a"

        title_map = {
            "curfew": "Alerta Parental: Toque de Queda Activo",
            "limit_reached": "Alerta Parental: Límite de Tiempo Alcanzado",
            "blocked_attempt": "Alerta Parental: Intento de Acceso a Contenido Inapropiado"
        }

        notif = NotificationModel(
            user_id=parent_user_id,
            sender_id=req.child_user_id,
            type="parental_curfew_alert" if req.alert_type == "curfew" else "parental_limit_exceeded",
            title=title_map.get(req.alert_type, "Notificación de Control Parental"),
            message=f"Aviso sobre la cuenta de {child_name}: {req.message}",
            resource_type="system",
            is_read=False
        )
        self.db.add(notif)
        self.db.commit()

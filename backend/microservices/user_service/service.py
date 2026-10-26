from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from backend.core.database import (
    UserModel, ParentalControlModel, VideoModel, FollowModel,
    VideoLikeModel, ParentChildLinkModel, NotificationModel
)
from backend.reglas.parental_control import ParentalControlManager
from backend.reglas.content_safety import ContentSafetyEngine, ModerationSeverity
from .schemas import (
    UserProfileUpdate, UserProfileView, SetParentalPinRequest,
    VerifyParentalPinRequest, ParentalSettingsUpdate, ParentalStatusResponse,
    PairChildRequest, ParentChildLinkResponse
)


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.safety_engine = ContentSafetyEngine()

    def get_profile_by_username(self, username: str, viewer_id: Optional[int] = None) -> UserProfileView:
        user = self.db.query(UserModel).filter(UserModel.username == username, UserModel.is_active == True).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario @{username} no encontrado.")

        # Conteo de seguidores y siguiendo
        followers_count = self.db.query(func.count(FollowModel.follower_id)).filter(FollowModel.following_id == user.id).scalar() or 0
        following_count = self.db.query(func.count(FollowModel.following_id)).filter(FollowModel.follower_id == user.id).scalar() or 0

        # Conteo de videos públicos y likes acumulados
        videos_count = self.db.query(func.count(VideoModel.id)).filter(
            VideoModel.user_id == user.id,
            VideoModel.moderation_status == "approved"
        ).scalar() or 0

        total_likes = self.db.query(func.sum(VideoModel.likes_count)).filter(
            VideoModel.user_id == user.id
        ).scalar() or 0

        is_following = False
        if viewer_id:
            is_following = bool(self.db.query(FollowModel).filter(
                FollowModel.follower_id == viewer_id,
                FollowModel.following_id == user.id
            ).first())

        return UserProfileView(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            is_verified=user.is_verified,
            is_private=user.is_private,
            followers_count=followers_count,
            following_count=following_count,
            videos_count=videos_count,
            likes_count=total_likes,
            is_following=is_following,
            created_at=user.created_at
        )

    def update_profile(self, user: UserModel, req: UserProfileUpdate) -> UserProfileView:
        if req.full_name is not None:
            user.full_name = req.full_name

        if req.bio is not None:
            # Evaluar que la biografía no contenga lenguaje ofensivo usando las reglas de seguridad
            scan = self.safety_engine.scan_text(req.bio)
            if scan.severity in (ModerationSeverity.CRITICAL, ModerationSeverity.HIGH):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="La biografía contiene términos que infringen las normas de la comunidad."
                )
            user.bio = scan.sanitized_text or req.bio

        if req.avatar_url is not None:
            user.avatar_url = req.avatar_url

        if req.is_private is not None:
            user.is_private = req.is_private

        self.db.commit()
        self.db.refresh(user)
        return self.get_profile_by_username(user.username, viewer_id=user.id)

    def toggle_follow(self, follower_id: int, target_user_id: int) -> dict:
        if follower_id == target_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes seguirte a ti mismo.")

        target = self.db.query(UserModel).filter(UserModel.id == target_user_id, UserModel.is_active == True).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario a seguir no existe.")

        existing = self.db.query(FollowModel).filter(
            FollowModel.follower_id == follower_id,
            FollowModel.following_id == target_user_id
        ).first()

        if existing:
            self.db.delete(existing)
            self.db.commit()
            return {"following": False, "message": f"Has dejado de seguir a @{target.username}"}
        else:
            follow_state = "pending" if target.is_private else "active"
            new_follow = FollowModel(follower_id=follower_id, following_id=target_user_id, status=follow_state)
            self.db.add(new_follow)

            # NOTIFICACIÓN AUTOMÁTICA: Notificar al usuario seguido
            follower_user = self.db.query(UserModel).filter(UserModel.id == follower_id).first()
            sender_name = follower_user.username if follower_user else "alguien"
            notif = NotificationModel(
                user_id=target_user_id,
                sender_id=follower_id,
                type="new_follower",
                title="¡Nuevo Seguidor!",
                message=f"@{sender_name} ha comenzado a seguirte.",
                resource_type="user",
                resource_id=follower_id,
                is_read=False
            )
            self.db.add(notif)
            self.db.commit()

            msg = f"Solicitud enviada a @{target.username}" if target.is_private else f"Ahora sigues a @{target.username}"
            return {"following": True, "status": follow_state, "message": msg}

    # --------------------------------------------------------------------------
    # MÉTODOS DE VINCULACIÓN FAMILIAR (PARENT - CHILD LINKS)
    # --------------------------------------------------------------------------
    def pair_child(self, parent_id: int, req: PairChildRequest) -> ParentChildLinkResponse:
        parent = self.db.query(UserModel).filter(UserModel.id == parent_id).first()
        child = self.db.query(UserModel).filter(UserModel.username == req.child_username.strip().lstrip('@')).first()

        if not child:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cuenta de menor @{req.child_username} no encontrada.")

        if child.id == parent_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes vincularte a ti mismo como hijo.")

        existing = self.db.query(ParentChildLinkModel).filter(
            ParentChildLinkModel.parent_user_id == parent_id,
            ParentChildLinkModel.child_user_id == child.id
        ).first()

        if existing:
            return ParentChildLinkResponse(
                link_id=existing.id,
                parent_id=existing.parent_user_id,
                child_id=existing.child_user_id,
                child_username=child.username,
                child_full_name=child.full_name,
                status=existing.status,
                created_at=existing.created_at
            )

        new_link = ParentChildLinkModel(
            parent_user_id=parent_id,
            child_user_id=child.id,
            status="active",
            linked_at=datetime.now(timezone.utc)
        )
        self.db.add(new_link)

        # Notificar al menor sobre la vinculación
        notif = NotificationModel(
            user_id=child.id,
            sender_id=parent_id,
            type="system_announcement",
            title="Vinculación Familiar Activada",
            message=f"La cuenta de @{parent.username} ha sido vinculada como tutor parental.",
            resource_type="system",
            is_read=False
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(new_link)

        return ParentChildLinkResponse(
            link_id=new_link.id,
            parent_id=new_link.parent_user_id,
            child_id=new_link.child_user_id,
            child_username=child.username,
            child_full_name=child.full_name,
            status=new_link.status,
            created_at=new_link.created_at
        )

    def get_linked_children(self, parent_id: int) -> List[ParentChildLinkResponse]:
        links = self.db.query(ParentChildLinkModel).filter(
            ParentChildLinkModel.parent_user_id == parent_id,
            ParentChildLinkModel.status == "active"
        ).all()

        results = []
        for l in links:
            child = l.child
            if child:
                results.append(ParentChildLinkResponse(
                    link_id=l.id,
                    parent_id=l.parent_user_id,
                    child_id=l.child_user_id,
                    child_username=child.username,
                    child_full_name=child.full_name,
                    status=l.status,
                    created_at=l.created_at
                ))
        return results

    # --------------------------------------------------------------------------
    # MÉTODOS DE CONTROL PARENTAL
    # --------------------------------------------------------------------------
    def get_or_create_parental_config(self, user_id: int) -> ParentalControlModel:
        config = self.db.query(ParentalControlModel).filter(ParentalControlModel.user_id == user_id).first()
        if not config:
            config = ParentalControlModel(
                user_id=user_id,
                is_enabled=False,
                restricted_mode=True,
                daily_screen_time_limit_minutes=120,
                block_direct_messages=True,
                filter_mature_comments=True
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config

    def set_parental_pin(self, user_id: int, req: SetParentalPinRequest) -> dict:
        config = self.get_or_create_parental_config(user_id)
        config.pin_hash = ParentalControlManager.hash_parental_pin(req.pin)
        config.pin_failed_attempts = 0
        config.pin_locked_until = None
        config.is_enabled = True
        self.db.commit()
        return {"message": "Código PIN de Control Parental establecido y activado exitosamente."}

    def verify_parental_pin(self, user_id: int, req: VerifyParentalPinRequest) -> dict:
        config = self.get_or_create_parental_config(user_id)
        if not config.pin_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay un código PIN configurado en esta cuenta."
            )

        valid, attempts, locked_until, msg = ParentalControlManager.verify_parental_pin(
            stored_hash=config.pin_hash,
            input_pin=req.pin,
            failed_attempts=config.pin_failed_attempts,
            locked_until=config.pin_locked_until
        )

        config.pin_failed_attempts = attempts
        config.pin_locked_until = locked_until
        self.db.commit()

        if not valid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)

        return {"verified": True, "message": msg}

    def update_parental_settings(self, user_id: int, req: ParentalSettingsUpdate) -> ParentalStatusResponse:
        config = self.get_or_create_parental_config(user_id)

        if req.is_enabled is not None:
            config.is_enabled = req.is_enabled
        if req.daily_screen_time_limit_minutes is not None:
            config.daily_screen_time_limit_minutes = req.daily_screen_time_limit_minutes
        if req.curfew_start_time is not None:
            config.curfew_start_time = req.curfew_start_time
        if req.curfew_end_time is not None:
            config.curfew_end_time = req.curfew_end_time
        if req.restricted_mode is not None:
            config.restricted_mode = req.restricted_mode
        if req.block_direct_messages is not None:
            config.block_direct_messages = req.block_direct_messages
        if req.filter_mature_comments is not None:
            config.filter_mature_comments = req.filter_mature_comments
        if req.allow_search is not None:
            config.allow_search = req.allow_search

        self.db.commit()
        self.db.refresh(config)

        return ParentalStatusResponse(
            is_enabled=config.is_enabled,
            has_pin_configured=bool(config.pin_hash),
            daily_screen_time_limit_minutes=config.daily_screen_time_limit_minutes,
            curfew_start_time=str(config.curfew_start_time) if config.curfew_start_time else None,
            curfew_end_time=str(config.curfew_end_time) if config.curfew_end_time else None,
            restricted_mode=config.restricted_mode,
            block_direct_messages=config.block_direct_messages,
            filter_mature_comments=config.filter_mature_comments,
            allow_search=config.allow_search
        )


from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.core.database import (
    VideoModel, UserModel, CommentModel, VideoLikeModel,
    SavedVideoModel, ParentalControlModel, ModerationAuditModel,
    NotificationModel, CommentLikeModel, VideoShareModel
)
from backend.reglas.rule_evaluator import rule_evaluator
from .schemas import (
    CommentCreateRequest, CommentResponse, CommentAuthor,
    LikeToggleResponse, BookmarkToggleResponse, ShareResponse,
    CommentLikeToggleResponse
)


class InteractionService:
    def __init__(self, db: Session):
        self.db = db

    def toggle_like(self, user: UserModel, video_id: int) -> LikeToggleResponse:
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        existing = self.db.query(VideoLikeModel).filter(
            VideoLikeModel.user_id == user.id,
            VideoLikeModel.video_id == video_id
        ).first()

        if existing:
            self.db.delete(existing)
            video.likes_count = max(0, video.likes_count - 1)
            is_liked = False
        else:
            new_like = VideoLikeModel(user_id=user.id, video_id=video_id)
            self.db.add(new_like)
            video.likes_count += 1
            is_liked = True

            # NOTIFICACIÓN AUTOMÁTICA: Si el like no es del mismo autor
            if video.user_id != user.id:
                notif = NotificationModel(
                    user_id=video.user_id,
                    sender_id=user.id,
                    type="new_like",
                    title="¡Nuevo Me Gusta!",
                    message=f"A @{user.username} le gustó tu video '{video.title[:35]}...'",
                    resource_type="video",
                    resource_id=video.id,
                    is_read=False
                )
                self.db.add(notif)

        self.db.commit()
        return LikeToggleResponse(video_id=video_id, is_liked=is_liked, total_likes=video.likes_count)

    def toggle_comment_like(self, user: UserModel, comment_id: int) -> CommentLikeToggleResponse:
        comment = self.db.query(CommentModel).filter(CommentModel.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado.")

        existing = self.db.query(CommentLikeModel).filter(
            CommentLikeModel.user_id == user.id,
            CommentLikeModel.comment_id == comment_id
        ).first()

        if existing:
            self.db.delete(existing)
            comment.likes_count = max(0, comment.likes_count - 1)
            is_liked = False
        else:
            new_like = CommentLikeModel(user_id=user.id, comment_id=comment_id)
            self.db.add(new_like)
            comment.likes_count += 1
            is_liked = True

            # NOTIFICACIÓN AUTOMÁTICA: Si no es su propio comentario
            if comment.user_id != user.id:
                notif = NotificationModel(
                    user_id=comment.user_id,
                    sender_id=user.id,
                    type="new_like",
                    title="Me gusta en tu comentario",
                    message=f"A @{user.username} le gustó tu comentario: '{comment.content[:35]}...'",
                    resource_type="comment",
                    resource_id=comment.id,
                    is_read=False
                )
                self.db.add(notif)

        self.db.commit()
        return CommentLikeToggleResponse(comment_id=comment_id, is_liked=is_liked, total_likes=comment.likes_count)

    def add_comment(self, user: UserModel, video_id: int, req: CommentCreateRequest) -> CommentResponse:
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        if not video.allow_comments:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El creador desactivó los comentarios para este video.")

        # Obtener configuración parental del autor del video
        author_parental = self.db.query(ParentalControlModel).filter(ParentalControlModel.user_id == video.user_id).first()
        filter_mature = author_parental.filter_mature_comments if author_parental else False

        # EVALUAR REGLA DE SEGURIDAD PARA COMENTARIOS
        evaluation = rule_evaluator.evaluate_comment(
            content=req.content,
            author_birth_date=user.birth_date,
            filter_mature_comments_for_video_author=filter_mature
        )

        if not evaluation.can_post:
            # Registrar comentario bloqueado en auditoría
            audit = ModerationAuditModel(
                target_type="comment",
                rule_triggered="prohibited_comment_block",
                severity_level="high",
                action_applied="auto_banned",
                reason=evaluation.reason,
                evaluated_text_snippet=req.content[:490]
            )
            self.db.add(audit)
            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Comentario bloqueado por las normas de la comunidad: {evaluation.reason}"
            )

        new_comment = CommentModel(
            video_id=video_id,
            user_id=user.id,
            parent_comment_id=req.parent_comment_id,
            content=evaluation.filtered_content,  # Guarda texto sanitizado/enmascarado si contenía palabras sensibles
            is_flagged=evaluation.is_flagged,
            moderation_status=evaluation.moderation_status
        )
        self.db.add(new_comment)
        video.comments_count += 1

        # NOTIFICACIÓN AUTOMÁTICA: Notificar al creador del video
        if video.user_id != user.id:
            notif = NotificationModel(
                user_id=video.user_id,
                sender_id=user.id,
                type="new_comment",
                title="Nuevo Comentario",
                message=f"@{user.username} comentó: '{evaluation.filtered_content[:45]}...'",
                resource_type="video",
                resource_id=video.id,
                is_read=False
            )
            self.db.add(notif)

        self.db.commit()
        self.db.refresh(new_comment)

        return self._format_comment(new_comment, viewer_id=user.id)

    def get_video_comments(self, video_id: int, viewer_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[CommentResponse]:
        comments = self.db.query(CommentModel).filter(
            CommentModel.video_id == video_id,
            CommentModel.moderation_status.in_(["approved", "flagged"])
        ).order_by(desc(CommentModel.created_at)).offset(offset).limit(limit).all()

        return [self._format_comment(c, viewer_id=viewer_id) for c in comments]

    def delete_comment(self, user: UserModel, comment_id: int):
        comment = self.db.query(CommentModel).filter(CommentModel.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado.")

        video = self.db.query(VideoModel).filter(VideoModel.id == comment.video_id).first()
        # El comentario solo puede ser borrado por su autor o por el autor del video
        if comment.user_id != user.id and (video and video.user_id != user.id) and user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este comentario.")

        self.db.delete(comment)
        if video and video.comments_count > 0:
            video.comments_count -= 1
        self.db.commit()

    def toggle_bookmark(self, user: UserModel, video_id: int) -> BookmarkToggleResponse:
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        existing = self.db.query(SavedVideoModel).filter(
            SavedVideoModel.user_id == user.id,
            SavedVideoModel.video_id == video_id
        ).first()

        if existing:
            self.db.delete(existing)
            video.saves_count = max(0, video.saves_count - 1)
            is_saved = False
        else:
            new_save = SavedVideoModel(user_id=user.id, video_id=video_id)
            self.db.add(new_save)
            video.saves_count += 1
            is_saved = True

        self.db.commit()
        return BookmarkToggleResponse(video_id=video_id, is_saved=is_saved, total_saves=video.saves_count)

    def record_share(self, video_id: int, platform: str = "link_copy", user: Optional[UserModel] = None) -> ShareResponse:
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        valid_platforms = ('whatsapp', 'facebook', 'instagram', 'twitter', 'link_copy', 'other')
        platform_normalized = platform.lower() if platform.lower() in valid_platforms else 'other'

        # Registrar fila en la tabla video_shares
        share_record = VideoShareModel(
            video_id=video.id,
            user_id=user.id if user else None,
            share_platform=platform_normalized
        )
        self.db.add(share_record)
        video.shares_count += 1
        self.db.commit()

        share_url = f"/videos/{video.id}"
        return ShareResponse(
            video_id=video.id,
            platform=platform_normalized,
            total_shares=video.shares_count,
            share_url=share_url
        )

    def _format_comment(self, comment: CommentModel, viewer_id: Optional[int] = None) -> CommentResponse:
        author = comment.user
        is_liked = False
        if viewer_id:
            is_liked = bool(self.db.query(CommentLikeModel).filter(
                CommentLikeModel.user_id == viewer_id,
                CommentLikeModel.comment_id == comment.id
            ).first())

        return CommentResponse(
            id=comment.id,
            video_id=comment.video_id,
            parent_comment_id=comment.parent_comment_id,
            content=comment.content,
            likes_count=comment.likes_count,
            is_liked_by_viewer=is_liked,
            is_flagged=comment.is_flagged,
            moderation_status=comment.moderation_status,
            author=CommentAuthor(
                id=author.id,
                username=author.username,
                full_name=author.full_name,
                avatar_url=author.avatar_url,
                is_verified=author.is_verified
            ),
            created_at=comment.created_at
        )


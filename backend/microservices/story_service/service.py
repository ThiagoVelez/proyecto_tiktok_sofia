"""
Lógica de Negocio del Microservicio de Historias (Stories)
Gestiona contenido efímero con expiración a las 24 horas, feed agrupado y telemetría de visualizaciones.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.core.database import (
    StoryModel, StoryViewModel, UserModel, ModerationAuditModel, ParentalControlModel
)
from backend.reglas.rule_evaluator import rule_evaluator
from backend.reglas.parental_control import ParentalControlManager
from .schemas import (
    StoryDetail, StoryAuthorSummary, UserStoriesGroup,
    StoryFeedResponse, StoryViewerItem, StoryViewersResponse
)


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class StoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_story(
        self,
        author: UserModel,
        media_url: str,
        media_type: str = "video",
        caption: Optional[str] = None,
        duration_seconds: float = 5.0
    ) -> StoryDetail:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=24)

        # 1. EVALUAR MODERACIÓN Y SEGURIDAD DEL CONTENIDO
        audience_rating = "all_ages"
        moderation_status = "approved"

        if caption:
            decision = rule_evaluator.evaluate_text(caption, author.birth_date)
            if not decision.can_publish:
                # Registrar auditoría de moderación
                audit = ModerationAuditModel(
                    target_type="video",  # Auditoría genérica multimedia
                    rule_triggered="story_moderation_block",
                    severity_level="high",
                    action_applied="auto_banned",
                    reason=decision.reason,
                    evaluated_text_snippet=caption[:490]
                )
                self.db.add(audit)
                self.db.commit()

                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Historia rechazada por seguridad de contenido: {decision.reason}"
                )

            if decision.detected_warnings:
                audience_rating = "teen" if decision.audience_rating.value in ("teen", "all_ages") else "mature"
                moderation_status = decision.moderation_status.value

        # 2. Persistir Historia en Base de Datos
        new_story = StoryModel(
            user_id=author.id,
            media_url=media_url,
            media_type=media_type if media_type in ("video", "image") else "video",
            caption=caption,
            duration_seconds=duration_seconds,
            audience_rating=audience_rating,
            moderation_status=moderation_status,
            views_count=0,
            expires_at=expires_at,
            created_at=now
        )
        self.db.add(new_story)
        self.db.commit()
        self.db.refresh(new_story)

        return self._format_story_detail(new_story, viewer_id=author.id)

    def get_active_feed(self, viewer: Optional[UserModel]) -> StoryFeedResponse:
        now = datetime.now(timezone.utc)

        # Consulta historias no expiradas y aprobadas
        query = (
            self.db.query(StoryModel)
            .filter(
                StoryModel.expires_at > now,
                StoryModel.moderation_status == "approved"
            )
            .order_by(StoryModel.created_at.asc())
        )

        # Filtro de control parental y protección de menores
        restricted_mode = True
        viewer_age = 13
        if viewer:
            viewer_age = ParentalControlManager.calculate_user_age(viewer.birth_date)
            parental = self.db.query(ParentalControlModel).filter(ParentalControlModel.user_id == viewer.id).first()
            if parental and parental.is_enabled:
                restricted_mode = parental.restricted_mode
            else:
                restricted_mode = viewer_age < 18

        if restricted_mode or viewer_age < 18:
            query = query.filter(StoryModel.audience_rating.in_(["all_ages", "teen"]))

        stories = query.all()

        if not stories:
            return StoryFeedResponse(total_authors=0, tray=[])

        # Obtener IDs de historias ya vistas por el espectador
        viewed_story_ids = set()
        if viewer:
            story_ids = [s.id for s in stories]
            views = (
                self.db.query(StoryViewModel.story_id)
                .filter(
                    StoryViewModel.viewer_user_id == viewer.id,
                    StoryViewModel.story_id.in_(story_ids)
                )
                .all()
            )
            viewed_story_ids = {v[0] for v in views}

        # Agrupar historias por autor
        groups: Dict[int, List[StoryModel]] = {}
        for story in stories:
            groups.setdefault(story.user_id, []).append(story)

        tray: List[UserStoriesGroup] = []
        viewer_id = viewer.id if viewer else None

        for user_id, user_story_list in groups.items():
            author = user_story_list[0].author
            formatted_stories = [
                self._format_story_detail(s, viewer_id=viewer_id, viewed_ids=viewed_story_ids)
                for s in user_story_list
            ]
            has_unseen = any(not s.is_viewed_by_viewer for s in formatted_stories)
            latest_at = max(s.created_at for s in user_story_list)

            tray.append(UserStoriesGroup(
                user_id=author.id,
                author=StoryAuthorSummary(
                    id=author.id,
                    username=author.username,
                    full_name=author.full_name,
                    avatar_url=author.avatar_url,
                    is_verified=author.is_verified
                ),
                stories_count=len(formatted_stories),
                has_unseen=has_unseen,
                latest_story_at=latest_at,
                stories=formatted_stories
            ))

        # Ordenar bandeja: primero el propio usuario si tiene historias, luego no vistas, luego más recientes
        def sort_key(group: UserStoriesGroup):
            is_own = 1 if viewer_id and group.user_id == viewer_id else 0
            unseen = 1 if group.has_unseen else 0
            ts = to_utc(group.latest_story_at).timestamp() if group.latest_story_at else 0
            return (is_own, unseen, ts)

        tray.sort(key=sort_key, reverse=True)

        return StoryFeedResponse(total_authors=len(tray), tray=tray)

    def get_user_stories(self, user_id: int, viewer: Optional[UserModel]) -> List[StoryDetail]:
        now = datetime.now(timezone.utc)
        stories = (
            self.db.query(StoryModel)
            .filter(
                StoryModel.user_id == user_id,
                StoryModel.expires_at > now,
                StoryModel.moderation_status == "approved"
            )
            .order_by(StoryModel.created_at.asc())
            .all()
        )

        viewed_ids = set()
        if viewer and stories:
            views = (
                self.db.query(StoryViewModel.story_id)
                .filter(
                    StoryViewModel.viewer_user_id == viewer.id,
                    StoryViewModel.story_id.in_([s.id for s in stories])
                )
                .all()
            )
            viewed_ids = {v[0] for v in views}

        viewer_id = viewer.id if viewer else None
        return [self._format_story_detail(s, viewer_id=viewer_id, viewed_ids=viewed_ids) for s in stories]

    def get_story_by_id(self, story_id: int, viewer: Optional[UserModel]) -> StoryDetail:
        story = self.db.query(StoryModel).filter(StoryModel.id == story_id).first()
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia no encontrada.")

        viewer_id = viewer.id if viewer else None
        return self._format_story_detail(story, viewer_id=viewer_id)

    def register_story_view(self, story_id: int, viewer: UserModel) -> dict:
        story = self.db.query(StoryModel).filter(StoryModel.id == story_id).first()
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia no encontrada.")

        now = datetime.now(timezone.utc)
        exp_utc = to_utc(story.expires_at)
        if exp_utc and exp_utc <= now:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta historia ya expiró.")

        # Si el autor ve su propia historia, no suma a métricas únicas
        if story.user_id == viewer.id:
            return {"story_id": story_id, "views_count": story.views_count, "already_viewed": True}

        existing_view = (
            self.db.query(StoryViewModel)
            .filter(
                StoryViewModel.story_id == story_id,
                StoryViewModel.viewer_user_id == viewer.id
            )
            .first()
        )

        if not existing_view:
            new_view = StoryViewModel(
                story_id=story_id,
                viewer_user_id=viewer.id,
                viewed_at=now
            )
            self.db.add(new_view)
            story.views_count += 1
            self.db.commit()
            return {"story_id": story_id, "views_count": story.views_count, "already_viewed": False}

        return {"story_id": story_id, "views_count": story.views_count, "already_viewed": True}

    def get_story_viewers(self, story_id: int, current_user: UserModel) -> StoryViewersResponse:
        story = self.db.query(StoryModel).filter(StoryModel.id == story_id).first()
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia no encontrada.")

        # Solo el creador o moderadores pueden ver la lista de espectadores
        if story.user_id != current_user.id and current_user.role not in ("admin", "moderator"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador o moderadores pueden ver la lista de espectadores de la historia."
            )

        views = (
            self.db.query(StoryViewModel)
            .filter(StoryViewModel.story_id == story_id)
            .order_by(desc(StoryViewModel.viewed_at))
            .all()
        )

        viewers_list: List[StoryViewerItem] = []
        for v in views:
            u = v.viewer
            if u:
                viewers_list.append(StoryViewerItem(
                    viewer_id=u.id,
                    username=u.username,
                    full_name=u.full_name,
                    avatar_url=u.avatar_url,
                    viewed_at=v.viewed_at
                ))

        return StoryViewersResponse(
            story_id=story.id,
            views_count=story.views_count,
            viewers=viewers_list
        )

    def delete_story(self, story_id: int, current_user: UserModel) -> dict:
        story = self.db.query(StoryModel).filter(StoryModel.id == story_id).first()
        if not story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia no encontrada.")

        if story.user_id != current_user.id and current_user.role not in ("admin", "moderator"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes autorización para eliminar esta historia."
            )

        self.db.delete(story)
        self.db.commit()
        return {"story_id": story_id, "deleted": True}

    def _format_story_detail(
        self,
        story: StoryModel,
        viewer_id: Optional[int] = None,
        viewed_ids: Optional[set] = None
    ) -> StoryDetail:
        now = datetime.now(timezone.utc)
        exp_utc = to_utc(story.expires_at)
        created_utc = to_utc(story.created_at) or now
        is_expired = exp_utc <= now if exp_utc else False

        is_viewed = False
        if viewer_id:
            if viewed_ids is not None:
                is_viewed = story.id in viewed_ids
            else:
                has_view = (
                    self.db.query(StoryViewModel)
                    .filter(
                        StoryViewModel.story_id == story.id,
                        StoryViewModel.viewer_user_id == viewer_id
                    )
                    .first()
                )
                is_viewed = bool(has_view)

        author = story.author
        return StoryDetail(
            id=story.id,
            user_id=story.user_id,
            media_url=story.media_url,
            media_type=story.media_type,
            caption=story.caption,
            duration_seconds=float(story.duration_seconds or 5.0),
            audience_rating=story.audience_rating,
            moderation_status=story.moderation_status,
            views_count=story.views_count,
            expires_at=exp_utc or now,
            created_at=created_utc,
            is_expired=is_expired,
            is_viewed_by_viewer=is_viewed,
            author=StoryAuthorSummary(
                id=author.id,
                username=author.username,
                full_name=author.full_name,
                avatar_url=author.avatar_url,
                is_verified=author.is_verified
            )
        )

from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.core.database import (
    VideoModel, UserModel, SoundModel, VideoLikeModel,
    SavedVideoModel, FollowModel, ModerationAuditModel,
    ParentalControlModel, HashtagModel, VideoHashtagModel,
    VideoViewModel, ScreenTimeSessionModel
)
from backend.core.exceptions import ParentalRestrictionException
from backend.reglas.rule_evaluator import rule_evaluator
from backend.reglas.parental_control import ParentalControlManager
from .schemas import VideoCreateRequest, VideoDetail, AuthorSummary, SoundResponse, FeedResponse


class VideoService:
    def __init__(self, db: Session):
        self.db = db

    def upload_video(self, author: UserModel, req: VideoCreateRequest) -> VideoDetail:
        # 1. EVALUAR REGLAS DE SEGURIDAD Y CONTROL PARENTAL
        decision = rule_evaluator.evaluate_new_video(
            title=req.title,
            description=req.description,
            hashtags=req.hashtags,
            author_birth_date=author.birth_date
        )

        if not decision.can_publish:
            # Registrar intento bloqueado en auditoría
            audit = ModerationAuditModel(
                target_type="video",
                rule_triggered="auto_moderation_block",
                severity_level="critical",
                action_applied="auto_banned",
                reason=decision.reason,
                evaluated_text_snippet=f"{req.title} - {req.description or ''}"[:490]
            )
            self.db.add(audit)
            self.db.commit()

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=decision.reason
            )

        # 2. Si fue retenido o tiene advertencias, auditar
        if decision.detected_warnings:
            audit = ModerationAuditModel(
                target_type="video",
                rule_triggered="content_warning_audit",
                severity_level="medium",
                action_applied="age_restricted" if decision.audience_rating.value in ("mature", "restricted") else "content_flagged",
                reason=decision.reason,
                evaluated_text_snippet=f"Keywords: {', '.join(decision.detected_warnings)}"
            )
            self.db.add(audit)

        # 3. Guardar el video
        new_video = VideoModel(
            user_id=author.id,
            sound_id=req.sound_id,
            title=req.title,
            description=req.description,
            video_url=req.video_url,
            thumbnail_url=req.thumbnail_url,
            duration_seconds=req.duration_seconds,
            visibility=req.visibility or "public",
            allow_comments=req.allow_comments if req.allow_comments is not None else True,
            allow_duet=req.allow_duet if req.allow_duet is not None else True,
            audience_rating=decision.audience_rating.value,
            moderation_status=decision.moderation_status.value,
            moderation_reason=decision.reason if decision.moderation_status.value != "approved" else None
        )
        self.db.add(new_video)
        self.db.commit()
        self.db.refresh(new_video)

        # 4. Procesar y vincular Hashtags
        if req.hashtags:
            for tag_raw in req.hashtags:
                clean_tag = tag_raw.strip().lstrip('#').lower()
                if not clean_tag:
                    continue
                tag_obj = self.db.query(HashtagModel).filter(HashtagModel.tag == clean_tag).first()
                if not tag_obj:
                    tag_obj = HashtagModel(tag=clean_tag, videos_count=1, views_count=0)
                    self.db.add(tag_obj)
                    self.db.flush()
                else:
                    tag_obj.videos_count += 1

                vh = VideoHashtagModel(video_id=new_video.id, hashtag_id=tag_obj.id)
                self.db.add(vh)

            self.db.commit()
            self.db.refresh(new_video)

        return self._format_video_detail(new_video, viewer_id=author.id)

    def get_for_you_feed(
        self,
        viewer: Optional[UserModel],
        limit: int = 15,
        offset: int = 0
    ) -> FeedResponse:
        screen_time_notice = None

        # 1. EVALUAR REGLAS PARENTALES DEL ESPECTADOR Y TELEMETRÍA DE TIEMPO
        restricted_mode = True
        viewer_age = 13  # Asumir menor por defecto si es anónimo para máxima seguridad de la audiencia
        consumed_today = 0

        if viewer:
            viewer_age = ParentalControlManager.calculate_user_age(viewer.birth_date)
            today = date.today()
            session = self.db.query(ScreenTimeSessionModel).filter(
                ScreenTimeSessionModel.user_id == viewer.id,
                ScreenTimeSessionModel.session_date == today
            ).first()
            if session:
                consumed_today = session.minutes_consumed

            parental = self.db.query(ParentalControlModel).filter(ParentalControlModel.user_id == viewer.id).first()

            if parental and parental.is_enabled:
                # Comprobar toque de queda (curfew) y límite de tiempo diario real
                evaluation = rule_evaluator.evaluate_feed_access(
                    user_birth_date=viewer.birth_date,
                    parental_enabled=parental.is_enabled,
                    daily_limit_minutes=parental.daily_screen_time_limit_minutes,
                    minutes_consumed_today=consumed_today,
                    curfew_start=parental.curfew_start_time,
                    curfew_end=parental.curfew_end_time
                )
                if not evaluation.is_allowed:
                    raise ParentalRestrictionException(detail=evaluation.message)

                restricted_mode = parental.restricted_mode
                screen_time_notice = evaluation.message
            else:
                restricted_mode = (viewer_age < 18)

        # 2. QUERY CON FILTRO DE AUDIENCIA ESTRICTO
        query = self.db.query(VideoModel).filter(
            VideoModel.moderation_status == "approved",
            VideoModel.visibility == "public"
        )

        # Si el modo restringido está activo o es menor de edad, solo videos 'all_ages' o 'teen'
        if restricted_mode or viewer_age < 18:
            allowed_ratings = ["all_ages"] if (restricted_mode or viewer_age < 13) else ["all_ages", "teen"]
            query = query.filter(VideoModel.audience_rating.in_(allowed_ratings))

        # 3. ALGORITMO DE RECOMENDACIÓN PARA TI (TikTok Engagement Score + Recencia)
        # Score ponderado: (Likes * 2) + (Comments * 3) + (Shares * 5) + (Views * 0.1)
        engagement_score = (
            VideoModel.likes_count * 2.0 +
            VideoModel.comments_count * 3.0 +
            VideoModel.shares_count * 5.0 +
            VideoModel.views_count * 0.1
        )
        videos = query.order_by(desc(engagement_score), desc(VideoModel.created_at)).offset(offset).limit(limit).all()
        viewer_id = viewer.id if viewer else None
        formatted_items = [self._format_video_detail(v, viewer_id) for v in videos]

        next_cursor = (offset + limit) if len(videos) == limit else None

        return FeedResponse(
            items=formatted_items,
            next_cursor=next_cursor,
            screen_time_notice=screen_time_notice
        )

    def get_following_feed(self, viewer: UserModel, limit: int = 15, offset: int = 0) -> FeedResponse:
        # Obtener IDs de usuarios seguidos
        following_ids = [
            f.following_id for f in self.db.query(FollowModel).filter(
                FollowModel.follower_id == viewer.id,
                FollowModel.status == "active"
            ).all()
        ]

        if not following_ids:
            return FeedResponse(items=[], next_cursor=None)

        videos = self.db.query(VideoModel).filter(
            VideoModel.user_id.in_(following_ids),
            VideoModel.moderation_status == "approved",
            VideoModel.visibility.in_(["public", "friends"])
        ).order_by(desc(VideoModel.created_at)).offset(offset).limit(limit).all()

        formatted_items = [self._format_video_detail(v, viewer.id) for v in videos]
        next_cursor = (offset + limit) if len(videos) == limit else None

        return FeedResponse(items=formatted_items, next_cursor=next_cursor)

    def get_video_by_id(self, video_id: int, viewer: Optional[UserModel] = None) -> VideoDetail:
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video no encontrado.")

        # Verificar permisos de audiencia
        if viewer:
            can_watch, reason = rule_evaluator.can_user_watch_video(
                user_birth_date=viewer.birth_date,
                parental_enabled=True,
                restricted_mode=False,
                video_rating=video.audience_rating,
                video_status=video.moderation_status
            )
            if not can_watch and reason:
                raise ParentalRestrictionException(detail=reason)

        viewer_id = viewer.id if viewer else None
        return self._format_video_detail(video, viewer_id)

    def register_view(
        self,
        video_id: int,
        viewer: Optional[UserModel] = None,
        duration_seconds: float = 0.0,
        watched_full: bool = False,
        ip_address: Optional[str] = None
    ):
        video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            return

        video.views_count += 1

        # Incrementar contador de vistas en hashtags vinculados
        if video.hashtags:
            for tag in video.hashtags:
                tag.views_count += 1

        # Registrar telemetría en tabla video_views
        view_log = VideoViewModel(
            video_id=video.id,
            user_id=viewer.id if viewer else None,
            watch_duration_seconds=duration_seconds,
            watched_full=watched_full,
            ip_address=ip_address
        )
        self.db.add(view_log)

        # Registrar minutos en sesión diaria de tiempo en pantalla si el usuario está autenticado
        if viewer and duration_seconds > 0:
            today = date.today()
            session = self.db.query(ScreenTimeSessionModel).filter(
                ScreenTimeSessionModel.user_id == viewer.id,
                ScreenTimeSessionModel.session_date == today
            ).first()
            added_minutes = max(1, int(round(duration_seconds / 60.0)))
            if session:
                session.minutes_consumed += added_minutes
                session.last_active_at = datetime.now(timezone.utc)
            else:
                session = ScreenTimeSessionModel(
                    user_id=viewer.id,
                    session_date=today,
                    minutes_consumed=added_minutes
                )
                self.db.add(session)

        self.db.commit()

    def _format_video_detail(self, video: VideoModel, viewer_id: Optional[int]) -> VideoDetail:
        author = video.author
        author_summary = AuthorSummary(
            id=author.id,
            username=author.username,
            full_name=author.full_name,
            avatar_url=author.avatar_url,
            is_verified=author.is_verified
        )

        sound_resp = None
        if video.sound:
            sound_resp = SoundResponse(
                id=video.sound.id,
                title=video.sound.title,
                artist_name=video.sound.artist_name,
                audio_url=video.sound.audio_url,
                cover_url=video.sound.cover_url,
                duration_seconds=video.sound.duration_seconds
            )

        is_liked = False
        is_saved = False
        if viewer_id:
            is_liked = bool(self.db.query(VideoLikeModel).filter(
                VideoLikeModel.user_id == viewer_id,
                VideoLikeModel.video_id == video.id
            ).first())
            is_saved = bool(self.db.query(SavedVideoModel).filter(
                SavedVideoModel.user_id == viewer_id,
                SavedVideoModel.video_id == video.id
            ).first())

        hashtag_tags = [h.tag for h in video.hashtags] if video.hashtags else []

        return VideoDetail(
            id=video.id,
            title=video.title,
            description=video.description,
            video_url=video.video_url,
            thumbnail_url=video.thumbnail_url,
            duration_seconds=float(video.duration_seconds),
            aspect_ratio=video.aspect_ratio,
            views_count=video.views_count,
            likes_count=video.likes_count,
            comments_count=video.comments_count,
            shares_count=video.shares_count,
            saves_count=video.saves_count,
            visibility=video.visibility,
            audience_rating=video.audience_rating,
            moderation_status=video.moderation_status,
            author=author_summary,
            sound=sound_resp,
            hashtags=hashtag_tags,
            is_liked_by_viewer=is_liked,
            is_saved_by_viewer=is_saved,
            created_at=video.created_at
        )


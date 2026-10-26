from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from backend.core.database import (
    VideoModel, UserModel, HashtagModel, SoundModel, FollowModel,
    ParentalControlModel
)
from backend.reglas.parental_control import ParentalControlManager
from backend.microservices.video_service.service import VideoService
from backend.microservices.video_service.schemas import VideoDetail, SoundResponse
from .schemas import SearchResultResponse, UserSearchItem, HashtagSummary


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.video_service = VideoService(db)

    def search_all(
        self,
        query: str,
        search_type: str = "all",
        viewer: Optional[UserModel] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResultResponse:
        clean_query = query.strip()
        result_videos: List[VideoDetail] = []
        result_users: List[UserSearchItem] = []
        result_hashtags: List[HashtagSummary] = []
        result_sounds: List[SoundResponse] = []

        # 1. Búsqueda de Videos
        if search_type in ("all", "videos"):
            result_videos = self.search_videos(clean_query, viewer=viewer, limit=limit, offset=offset)

        # 2. Búsqueda de Usuarios / Creadores
        if search_type in ("all", "users"):
            result_users = self.search_users(clean_query, limit=limit, offset=offset)

        # 3. Búsqueda de Hashtags
        if search_type in ("all", "hashtags"):
            result_hashtags = self.search_hashtags(clean_query, limit=limit, offset=offset)

        # 4. Búsqueda de Sonidos
        if search_type in ("all", "sounds"):
            result_sounds = self.search_sounds(clean_query, limit=limit, offset=offset)

        return SearchResultResponse(
            query=clean_query,
            search_type=search_type,
            videos=result_videos,
            users=result_users,
            hashtags=result_hashtags,
            sounds=result_sounds
        )

    def search_videos(
        self,
        query: str,
        viewer: Optional[UserModel] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[VideoDetail]:
        search_pattern = f"%{query}%"
        db_query = self.db.query(VideoModel).filter(
            VideoModel.moderation_status == "approved",
            VideoModel.visibility == "public",
            or_(
                VideoModel.title.ilike(search_pattern),
                VideoModel.description.ilike(search_pattern)
            )
        )

        # Filtro de audiencia y modo restringido según viewer
        restricted = True
        viewer_age = 13
        if viewer:
            viewer_age = ParentalControlManager.calculate_user_age(viewer.birth_date)
            parental = self.db.query(ParentalControlModel).filter(ParentalControlModel.user_id == viewer.id).first()
            restricted = parental.restricted_mode if parental and parental.is_enabled else (viewer_age < 18)

        if restricted or viewer_age < 18:
            allowed = ["all_ages"] if (restricted or viewer_age < 13) else ["all_ages", "teen"]
            db_query = db_query.filter(VideoModel.audience_rating.in_(allowed))

        videos = db_query.order_by(desc(VideoModel.views_count), desc(VideoModel.created_at)).offset(offset).limit(limit).all()
        viewer_id = viewer.id if viewer else None
        return [self.video_service._format_video_detail(v, viewer_id) for v in videos]

    def search_users(self, query: str, limit: int = 20, offset: int = 0) -> List[UserSearchItem]:
        clean_tag = query.lstrip('@')
        pattern = f"%{clean_tag}%"
        users = self.db.query(UserModel).filter(
            UserModel.is_active == True,
            or_(
                UserModel.username.ilike(pattern),
                UserModel.full_name.ilike(pattern)
            )
        ).offset(offset).limit(limit).all()

        results = []
        for u in users:
            followers_count = self.db.query(func.count(FollowModel.follower_id)).filter(
                FollowModel.following_id == u.id,
                FollowModel.status == "active"
            ).scalar() or 0

            results.append(UserSearchItem(
                id=u.id,
                username=u.username,
                full_name=u.full_name,
                avatar_url=u.avatar_url,
                is_verified=u.is_verified,
                followers_count=followers_count
            ))
        return results

    def search_hashtags(self, query: str, limit: int = 20, offset: int = 0) -> List[HashtagSummary]:
        clean_tag = query.lstrip('#')
        pattern = f"%{clean_tag}%"
        hashtags = self.db.query(HashtagModel).filter(
            HashtagModel.is_banned == False,
            HashtagModel.tag.ilike(pattern)
        ).order_by(desc(HashtagModel.videos_count), desc(HashtagModel.views_count)).offset(offset).limit(limit).all()

        return [
            HashtagSummary(
                id=h.id,
                tag=h.tag,
                videos_count=h.videos_count,
                views_count=h.views_count
            ) for h in hashtags
        ]

    def search_sounds(self, query: str, limit: int = 20, offset: int = 0) -> List[SoundResponse]:
        pattern = f"%{query}%"
        sounds = self.db.query(SoundModel).filter(
            SoundModel.is_active == True,
            or_(
                SoundModel.title.ilike(pattern),
                SoundModel.artist_name.ilike(pattern)
            )
        ).order_by(desc(SoundModel.usage_count)).offset(offset).limit(limit).all()

        return [
            SoundResponse(
                id=s.id,
                title=s.title,
                artist_name=s.artist_name,
                audio_url=s.audio_url,
                cover_url=s.cover_url,
                duration_seconds=s.duration_seconds
            ) for s in sounds
        ]

    def get_trending_hashtags(self, limit: int = 15) -> List[HashtagSummary]:
        tags = self.db.query(HashtagModel).filter(
            HashtagModel.is_banned == False
        ).order_by(desc(HashtagModel.videos_count), desc(HashtagModel.views_count)).limit(limit).all()

        return [
            HashtagSummary(
                id=h.id,
                tag=h.tag,
                videos_count=h.videos_count,
                views_count=h.views_count
            ) for h in tags
        ]

    def get_popular_sounds(self, limit: int = 15) -> List[SoundResponse]:
        sounds = self.db.query(SoundModel).filter(
            SoundModel.is_active == True
        ).order_by(desc(SoundModel.usage_count)).limit(limit).all()

        return [
            SoundResponse(
                id=s.id,
                title=s.title,
                artist_name=s.artist_name,
                audio_url=s.audio_url,
                cover_url=s.cover_url,
                duration_seconds=s.duration_seconds
            ) for s in sounds
        ]

    def get_videos_by_hashtag(
        self,
        hashtag: str,
        viewer: Optional[UserModel] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[VideoDetail]:
        clean_tag = hashtag.strip().lstrip('#').lower()
        tag_obj = self.db.query(HashtagModel).filter(HashtagModel.tag == clean_tag).first()
        if not tag_obj:
            return []

        videos = [v for v in tag_obj.videos if v.moderation_status == "approved" and v.visibility == "public"]
        viewer_id = viewer.id if viewer else None
        return [self.video_service._format_video_detail(v, viewer_id) for v in videos[offset:offset + limit]]

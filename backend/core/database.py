"""
Gestor de Conexión a Base de Datos MySQL y Modelos ORM
Cumple con el principio de Inversión de Dependencias (DIP) y gestión segura de transacciones.
"""

from datetime import datetime, date, time, timezone
from typing import Generator
from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, String, Text,
    Boolean, DateTime, Date, Time, ForeignKey, Enum as SQLEnum,
    Numeric
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from .config import settings

def utc_now():
    return datetime.now(timezone.utc)

# Engine con Connection Pooling y reconexión automática pre_ping
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Inyección de dependencias para sesiones de base de datos en endpoints FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# MODELOS ORM (Espejo completo del script backend/sql/schema.sql - 19 Tablas)
# ==============================================================================

from sqlalchemy.dialects.mysql import BIGINT as MySQL_BIGINT

# PK y FK compatibles tanto con MySQL 8 (BIGINT UNSIGNED) como con SQLite en memoria (INTEGER)
PK_ID = BigInteger().with_variant(MySQL_BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")
FK_ID = BigInteger().with_variant(MySQL_BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone_number = Column(String(25), nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    bio = Column(String(250), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    birth_date = Column(Date, nullable=False, index=True)
    role = Column(SQLEnum('user', 'creator', 'moderator', 'admin', name='user_roles'), default='user', nullable=False)
    account_type = Column(SQLEnum('standard', 'minor', 'parent', name='account_types'), default='standard', nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relaciones
    parental_control = relationship("ParentalControlModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    videos = relationship("VideoModel", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("CommentModel", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("VideoLikeModel", back_populates="user", cascade="all, delete-orphan")
    comment_likes = relationship("CommentLikeModel", back_populates="user", cascade="all, delete-orphan")
    shares = relationship("VideoShareModel", back_populates="user")
    views = relationship("VideoViewModel", back_populates="user")
    stories = relationship("StoryModel", back_populates="author", cascade="all, delete-orphan")


class ParentalControlModel(Base):
    __tablename__ = "parental_controls"

    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_enabled = Column(Boolean, default=False, nullable=False)
    pin_hash = Column(String(255), nullable=True)
    pin_failed_attempts = Column(Integer, default=0, nullable=False)
    pin_locked_until = Column(DateTime, nullable=True)
    daily_screen_time_limit_minutes = Column(Integer, default=120, nullable=False)
    curfew_start_time = Column(Time, default=time(22, 0), nullable=True)
    curfew_end_time = Column(Time, default=time(6, 0), nullable=True)
    restricted_mode = Column(Boolean, default=True, nullable=False)
    block_direct_messages = Column(Boolean, default=True, nullable=False)
    filter_mature_comments = Column(Boolean, default=True, nullable=False)
    allow_search = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="parental_control")


class ParentChildLinkModel(Base):
    __tablename__ = "parent_child_links"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    parent_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    child_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pairing_code = Column(String(20), nullable=True)
    status = Column(SQLEnum('pending', 'active', 'revoked', name='parent_child_status'), default='pending', nullable=False)
    linked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    parent = relationship("UserModel", foreign_keys=[parent_user_id])
    child = relationship("UserModel", foreign_keys=[child_user_id])


class ScreenTimeSessionModel(Base):
    __tablename__ = "screen_time_sessions"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False)
    minutes_consumed = Column(Integer, default=0, nullable=False)
    last_active_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel")


class SoundModel(Base):
    __tablename__ = "sounds"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    artist_name = Column(String(100), default="Sonido Original", nullable=False)
    audio_url = Column(String(500), nullable=False)
    cover_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, default=60, nullable=False)
    is_original = Column(Boolean, default=True, nullable=False)
    author_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    usage_count = Column(BigInteger, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    videos = relationship("VideoModel", back_populates="sound")
    author = relationship("UserModel", foreign_keys=[author_user_id])


class HashtagModel(Base):
    __tablename__ = "hashtags"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    tag = Column(String(100), unique=True, nullable=False, index=True)
    videos_count = Column(BigInteger, default=0, nullable=False)
    views_count = Column(BigInteger, default=0, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    videos = relationship("VideoModel", secondary="video_hashtags", back_populates="hashtags")


class VideoHashtagModel(Base):
    __tablename__ = "video_hashtags"

    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True)
    hashtag_id = Column(FK_ID, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True)


class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sound_id = Column(FK_ID, ForeignKey("sounds.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=False)
    duration_seconds = Column(Numeric(6, 2), default=15.0, nullable=False)
    aspect_ratio = Column(String(10), default="9:16", nullable=False)
    views_count = Column(BigInteger, default=0, nullable=False)
    likes_count = Column(BigInteger, default=0, nullable=False)
    comments_count = Column(BigInteger, default=0, nullable=False)
    shares_count = Column(BigInteger, default=0, nullable=False)
    saves_count = Column(BigInteger, default=0, nullable=False)
    visibility = Column(SQLEnum('public', 'friends', 'private', name='video_visibility'), default='public', nullable=False)
    allow_comments = Column(Boolean, default=True, nullable=False)
    allow_duet = Column(Boolean, default=True, nullable=False)
    allow_stitch = Column(Boolean, default=True, nullable=False)
    allow_download = Column(Boolean, default=True, nullable=False)
    audience_rating = Column(SQLEnum('all_ages', 'teen', 'mature', 'restricted', name='audience_ratings'), default='all_ages', nullable=False)
    moderation_status = Column(SQLEnum('approved', 'under_review', 'flagged', 'hidden', 'banned', name='mod_statuses'), default='approved', nullable=False)
    moderation_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    author = relationship("UserModel", back_populates="videos")
    sound = relationship("SoundModel", back_populates="videos")
    comments = relationship("CommentModel", back_populates="video", cascade="all, delete-orphan")
    likes = relationship("VideoLikeModel", back_populates="video", cascade="all, delete-orphan")
    hashtags = relationship("HashtagModel", secondary="video_hashtags", back_populates="videos")
    shares = relationship("VideoShareModel", back_populates="video", cascade="all, delete-orphan")
    views_details = relationship("VideoViewModel", back_populates="video", cascade="all, delete-orphan")


class VideoLikeModel(Base):
    __tablename__ = "video_likes"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="likes")
    video = relationship("VideoModel", back_populates="likes")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id = Column(FK_ID, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(String(1000), nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    moderation_status = Column(SQLEnum('approved', 'flagged', 'hidden', 'banned', name='comment_mod_status'), default='approved', nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="comments")
    video = relationship("VideoModel", back_populates="comments")
    likes = relationship("CommentLikeModel", back_populates="comment", cascade="all, delete-orphan")


class CommentLikeModel(Base):
    __tablename__ = "comment_likes"

    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    comment_id = Column(FK_ID, ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="comment_likes")
    comment = relationship("CommentModel", back_populates="likes")


class FollowModel(Base):
    __tablename__ = "follows"

    follower_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    following_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    status = Column(SQLEnum('active', 'pending', name='follow_status'), default='active', nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class SavedVideoModel(Base):
    __tablename__ = "saved_videos"

    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True)
    collection_name = Column(String(50), default="Favoritos", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class VideoShareModel(Base):
    __tablename__ = "video_shares"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    share_platform = Column(
        SQLEnum('whatsapp', 'facebook', 'instagram', 'twitter', 'link_copy', 'other', name='share_platforms'),
        default='link_copy',
        nullable=False
    )
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="shares")
    video = relationship("VideoModel", back_populates="shares")


class VideoViewModel(Base):
    __tablename__ = "video_views"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    video_id = Column(FK_ID, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    watch_duration_seconds = Column(Numeric(6, 2), default=0.00, nullable=False)
    watched_full = Column(Boolean, default=False, nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel", back_populates="views")
    video = relationship("VideoModel", back_populates="views_details")


class ContentReportModel(Base):
    __tablename__ = "content_reports"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    reporter_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_type = Column(SQLEnum('video', 'comment', 'user', name='report_target_type'), nullable=False)
    target_id = Column(BigInteger, nullable=False)
    reason_category = Column(SQLEnum(
        'inappropriate_for_minors', 'violence_graphic', 'hate_speech',
        'harassment_bullying', 'sexual_content', 'spam_scam',
        'self_harm', 'copyright_violation', 'other',
        name='report_reasons'
    ), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(SQLEnum('pending', 'under_review', 'resolved_action_taken', 'dismissed', name='report_statuses'), default='pending', nullable=False)
    moderator_notes = Column(Text, nullable=True)
    resolved_by_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class ModerationAuditModel(Base):
    __tablename__ = "moderation_audits"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    target_type = Column(SQLEnum('video', 'comment', 'user_profile', 'search_query', name='audit_targets'), nullable=False)
    target_id = Column(BigInteger, nullable=True)
    rule_triggered = Column(String(100), nullable=False)
    severity_level = Column(SQLEnum('low', 'medium', 'high', 'critical', name='audit_severities'), nullable=False)
    action_applied = Column(SQLEnum('none', 'content_flagged', 'age_restricted', 'auto_hidden', 'auto_banned', 'queued_review', name='audit_actions'), nullable=False)
    reason = Column(String(255), nullable=False)
    evaluated_text_snippet = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(FK_ID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    type = Column(SQLEnum(
        'new_like', 'new_comment', 'new_follower', 'mention',
        'parental_curfew_alert', 'parental_limit_exceeded',
        'moderation_warning', 'system_announcement',
        name='notification_types'
    ), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    resource_type = Column(SQLEnum('video', 'comment', 'user', 'system', name='resource_types'), nullable=True)
    resource_id = Column(BigInteger, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel", foreign_keys=[user_id])
    sender = relationship("UserModel", foreign_keys=[sender_id])


class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("UserModel")


class StoryModel(Base):
    __tablename__ = "stories"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    media_url = Column(String(500), nullable=False)
    media_type = Column(SQLEnum('video', 'image', name='story_media_types'), default='video', nullable=False)
    caption = Column(String(300), nullable=True)
    duration_seconds = Column(Numeric(5, 2), default=5.00, nullable=False)
    audience_rating = Column(SQLEnum('all_ages', 'teen', 'mature', 'restricted', name='story_audience_ratings'), default='all_ages', nullable=False)
    moderation_status = Column(SQLEnum('approved', 'under_review', 'rejected', name='story_moderation_statuses'), default='approved', nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    author = relationship("UserModel", back_populates="stories")
    views = relationship("StoryViewModel", back_populates="story", cascade="all, delete-orphan")


class StoryViewModel(Base):
    __tablename__ = "story_views"

    id = Column(PK_ID, primary_key=True, autoincrement=True)
    story_id = Column(FK_ID, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    viewer_user_id = Column(FK_ID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_at = Column(DateTime, default=utc_now, nullable=False)

    story = relationship("StoryModel", back_populates="views")
    viewer = relationship("UserModel")

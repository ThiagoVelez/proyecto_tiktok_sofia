"""
Módulo de Reglas: Evaluador Unificado (Facade de Reglas del Sistema)
Proyecto Sofía - Plataforma de Videos Cortos (TikTok-like)

Punto de entrada centralizado para aplicar todas las reglas del sistema:
- Moderación de videos
- Moderación de comentarios
- Reglas de control parental de visualización y tiempo
- Protección contra interacciones no deseadas a menores
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, date, time

from .parental_control import ParentalControlManager, ScreenTimeEvaluation, ParentalStatus
from .content_safety import ContentSafetyEngine, SafetyScanResult, ModerationSeverity, ModerationAction
from .audience_protection import AudienceProtectionSystem, VideoSafetyDecision, AudienceRating, VideoModerationStatus


@dataclass
class CommentEvaluation:
    can_post: bool
    moderation_status: str
    filtered_content: str
    is_flagged: bool
    reason: str


class SystemRuleEvaluator:
    """
    Fachada que orquesta el conjunto de reglas del backend de Sofía.
    Garantiza que ningún componente tenga que preocuparse por la lógica de reglas interna.
    """

    def __init__(self):
        self.safety_engine = ContentSafetyEngine()
        self.audience_system = AudienceProtectionSystem(self.safety_engine)
        self.parental_manager = ParentalControlManager()

    # --------------------------------------------------------------------------
    # 1. Reglas para Publicación de Videos
    # --------------------------------------------------------------------------
    def evaluate_new_video(
        self,
        title: str,
        description: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        author_birth_date: Optional[date] = None
    ) -> VideoSafetyDecision:
        """
        Analiza un video entrante antes de guardarlo en base de datos.
        """
        is_minor = False
        if author_birth_date:
            age = self.parental_manager.calculate_user_age(author_birth_date)
            is_minor = age < 18

        return self.audience_system.evaluate_video_metadata(
            title=title,
            description=description,
            hashtags=hashtags,
            author_is_minor=is_minor
        )

    # --------------------------------------------------------------------------
    # 2. Reglas para Publicación de Comentarios
    # --------------------------------------------------------------------------
    def evaluate_comment(
        self,
        content: str,
        author_birth_date: Optional[date] = None,
        filter_mature_comments_for_video_author: bool = False
    ) -> CommentEvaluation:
        """
        Analiza un comentario para filtrar agresiones, lenguaje ofensivo o spam.
        """
        is_minor = False
        if author_birth_date:
            age = self.parental_manager.calculate_user_age(author_birth_date)
            is_minor = age < 18

        scan = self.safety_engine.scan_text(content, user_is_minor=is_minor)

        # Si el autor del video o el usuario tiene activado 'filter_mature_comments',
        # enmascaramos o rechazamos comentarios de riesgo
        if scan.severity in (ModerationSeverity.CRITICAL, ModerationSeverity.HIGH):
            return CommentEvaluation(
                can_post=False,
                moderation_status="banned",
                filtered_content=scan.sanitized_text or content,
                is_flagged=True,
                reason=scan.reason
            )

        if scan.severity in (ModerationSeverity.MEDIUM, ModerationSeverity.LOW):
            # Se permite el comentario pero con palabras inapropiadas censuradas (p***a)
            return CommentEvaluation(
                can_post=True,
                moderation_status="flagged" if scan.severity == ModerationSeverity.MEDIUM else "approved",
                filtered_content=scan.sanitized_text or content,
                is_flagged=True,
                reason="El comentario contiene palabras que han sido suavizadas automáticamente."
            )

        return CommentEvaluation(
            can_post=True,
            moderation_status="approved",
            filtered_content=content,
            is_flagged=False,
            reason="Comentario apropiado."
        )

    # --------------------------------------------------------------------------
    # 3. Reglas de Visualización del Feed y Control Parental
    # --------------------------------------------------------------------------
    def evaluate_feed_access(
        self,
        user_birth_date: date,
        parental_enabled: bool,
        daily_limit_minutes: int,
        minutes_consumed_today: int,
        curfew_start: Optional[time],
        curfew_end: Optional[time]
    ) -> ScreenTimeEvaluation:
        """
        Evalúa si el usuario puede acceder a ver videos según sus límites de tiempo y descanso.
        """
        if not parental_enabled:
            return ScreenTimeEvaluation(
                is_allowed=True,
                status=ParentalStatus.ALLOWED,
                minutes_consumed=minutes_consumed_today,
                daily_limit=9999,
                minutes_remaining=9999,
                curfew_active=False,
                message="Sin restricciones parentales activas."
            )

        return self.parental_manager.evaluate_screen_time(
            daily_limit_minutes=daily_limit_minutes,
            minutes_consumed_today=minutes_consumed_today,
            curfew_start=curfew_start,
            curfew_end=curfew_end
        )

    def can_user_watch_video(
        self,
        user_birth_date: date,
        parental_enabled: bool,
        restricted_mode: bool,
        video_rating: str,
        video_status: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Determina si un usuario en específico tiene autorización de ver un video determinado.
        """
        user_age = self.parental_manager.calculate_user_age(user_birth_date)
        is_minor = user_age < 18

        if not self.audience_system.filter_feed_for_viewer(
            video_rating=video_rating,
            video_status=video_status,
            viewer_age=user_age,
            restricted_mode=restricted_mode
        ):
            return False, "Este contenido está restringido según las políticas de audiencia o configuración de control parental de tu cuenta."

        return self.parental_manager.can_access_video_by_age_and_mode(
            user_age=user_age,
            is_minor_account=is_minor,
            restricted_mode_enabled=restricted_mode,
            video_rating=video_rating
        )

    # --------------------------------------------------------------------------
    # 5. Reglas para Publicación de Historias (Stories)
    # --------------------------------------------------------------------------
    def evaluate_story(
        self,
        caption: Optional[str] = None,
        author_birth_date: Optional[date] = None
    ) -> VideoSafetyDecision:
        """
        Analiza el pie de foto / texto de una historia temporal antes de publicarla.
        """
        is_minor = False
        if author_birth_date:
            age = self.parental_manager.calculate_user_age(author_birth_date)
            is_minor = age < 18

        if not caption or not caption.strip():
            return VideoSafetyDecision(
                can_publish=True,
                audience_rating=AudienceRating.ALL_AGES,
                moderation_status=VideoModerationStatus.APPROVED,
                reason="Historia sin texto, aprobada para toda la audiencia.",
                detected_warnings=[]
            )

        return self.audience_system.evaluate_video_metadata(
            title=caption,
            description=None,
            hashtags=None,
            author_is_minor=is_minor
        )

    def evaluate_text(
        self,
        text: str,
        author_birth_date: Optional[date] = None
    ) -> VideoSafetyDecision:
        """Alias para evaluar texto de historias u otros recursos."""
        return self.evaluate_story(caption=text, author_birth_date=author_birth_date)


# Instancia singleton para uso rápido en microservicios
rule_evaluator = SystemRuleEvaluator()

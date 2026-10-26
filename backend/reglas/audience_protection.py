"""
Módulo de Reglas: Clasificación y Protección de Audiencia
Proyecto Sofía - Plataforma de Videos Cortos (TikTok-like)

Define las reglas de clasificación por edades de los videos y la política de distribución
en el feed 'Para Ti' (For You) para evitar que contenidos no deseados alcancen a menores
o audiencias sensibles.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .content_safety import ContentSafetyEngine, ModerationSeverity, ModerationAction


class AudienceRating(str, Enum):
    ALL_AGES = "all_ages"    # Apto para todo público / Familias
    TEEN = "teen"            # Apto para adolescentes (+13)
    MATURE = "mature"        # Contenido adulto / Temas maduros (+18)
    RESTRICTED = "restricted"# Contenido restringido / Solo mayores con confirmación


class VideoModerationStatus(str, Enum):
    APPROVED = "approved"
    UNDER_REVIEW = "under_review"
    FLAGGED = "flagged"
    HIDDEN = "hidden"
    BANNED = "banned"


@dataclass
class VideoSafetyDecision:
    can_publish: bool
    audience_rating: AudienceRating
    moderation_status: VideoModerationStatus
    reason: str
    detected_warnings: List[str]
    allow_recommendation_feed: bool


class AudienceProtectionSystem:
    """
    Sistema encargado de clasificar la audiencia de los videos y proteger a la comunidad
    antes y después de su publicación.
    """

    def __init__(self, safety_engine: Optional[ContentSafetyEngine] = None):
        self.safety_engine = safety_engine or ContentSafetyEngine()

    def evaluate_video_metadata(
        self,
        title: str,
        description: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        author_is_minor: bool = False
    ) -> VideoSafetyDecision:
        """
        Evalúa el título, descripción y etiquetas de un video para definir su calificación
        y estado de moderación antes de hacerlo visible.
        """
        full_text = f"{title} {description or ''} {' '.join(hashtags or [])}".strip()
        scan = self.safety_engine.scan_text(full_text, user_is_minor=author_is_minor)

        # Regla 1: Contenido con severidad crítica (bloqueo total)
        if scan.severity == ModerationSeverity.CRITICAL:
            return VideoSafetyDecision(
                can_publish=False,
                audience_rating=AudienceRating.RESTRICTED,
                moderation_status=VideoModerationStatus.BANNED,
                reason=f"Publicación rechazada automáticamente: {scan.reason}",
                detected_warnings=scan.detected_keywords,
                allow_recommendation_feed=False
            )

        # Regla 2: Contenido de alta severidad (oculto y retenido para revisión humana)
        if scan.severity == ModerationSeverity.HIGH:
            return VideoSafetyDecision(
                can_publish=False,
                audience_rating=AudienceRating.RESTRICTED,
                moderation_status=VideoModerationStatus.UNDER_REVIEW,
                reason=f"Publicación retenida para revisión: {scan.reason}",
                detected_warnings=scan.detected_keywords,
                allow_recommendation_feed=False
            )

        # Regla 3: Severidad media (permitido pero clasificado como maduro/18+)
        if scan.severity == ModerationSeverity.MEDIUM:
            return VideoSafetyDecision(
                can_publish=True,
                audience_rating=AudienceRating.MATURE,
                moderation_status=VideoModerationStatus.APPROVED,
                reason="El video contiene lenguaje o temáticas adolescentes/maduras. Clasificado para mayores de edad.",
                detected_warnings=scan.detected_keywords,
                allow_recommendation_feed=False  # No sugerir agresivamente en feed general
            )

        # Regla 4: Severidad baja (lenguaje coloquial/teen)
        if scan.severity == ModerationSeverity.LOW:
            return VideoSafetyDecision(
                can_publish=True,
                audience_rating=AudienceRating.TEEN,
                moderation_status=VideoModerationStatus.APPROVED,
                reason="Video clasificado para audiencia adolescente y adultos.",
                detected_warnings=scan.detected_keywords,
                allow_recommendation_feed=True
            )

        # Regla 5: Totalmente limpio
        return VideoSafetyDecision(
            can_publish=True,
            audience_rating=AudienceRating.ALL_AGES,
            moderation_status=VideoModerationStatus.APPROVED,
            reason="Video apto para todo público y compatible con Modo Restringido.",
            detected_warnings=[],
            allow_recommendation_feed=True
        )

    @staticmethod
    def filter_feed_for_viewer(
        video_rating: str,
        video_status: str,
        viewer_age: int,
        restricted_mode: bool = False
    ) -> bool:
        """
        Determina si un video puede ser mostrado en el feed del espectador según su perfil de seguridad.
        """
        # Si el video está baneado u oculto, nadie lo ve excepto su autor o moderadores
        if video_status in ("banned", "hidden", "under_review"):
            return False

        # Si el espectador tiene modo restringido activo (o es menor de 13 años), solo ve 'all_ages'
        if restricted_mode or viewer_age < 13:
            return video_rating == "all_ages"

        # Si el espectador tiene entre 13 y 17 años, puede ver 'all_ages' y 'teen'
        if viewer_age < 18:
            return video_rating in ("all_ages", "teen")

        # Adultos sin restricciones ven todo lo aprobado
        return True

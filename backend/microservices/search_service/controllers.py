from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user_optional
from backend.core.response import ApiResponse
from backend.microservices.video_service.schemas import VideoDetail, SoundResponse
from .schemas import SearchResultResponse, HashtagSummary
from .service import SearchService

router = APIRouter(prefix="/search", tags=["Búsqueda y Exploración"])


@router.get("", response_model=ApiResponse[SearchResultResponse])
def search_content(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    type: str = Query("all", description="all, videos, users, hashtags, sounds"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Barra de búsqueda global para la plataforma.
    Busca videos (por título y descripción), creadores (por usuario y nombre),
    hashtags y pistas de sonido simultáneamente.
    """
    service = SearchService(db)
    result = service.search_all(
        query=q,
        search_type=type,
        viewer=viewer,
        limit=limit,
        offset=offset
    )
    return ApiResponse.success_response(data=result, message="Búsqueda completada.")


@router.get("/hashtags/trending", response_model=ApiResponse[List[HashtagSummary]])
def get_trending_hashtags(
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Lista los hashtags más populares en tendencia ordenados por cantidad de videos y reproducciones."""
    service = SearchService(db)
    trending = service.get_trending_hashtags(limit=limit)
    return ApiResponse.success_response(data=trending, message="Tendencias obtenidas.")


@router.get("/sounds/popular", response_model=ApiResponse[List[SoundResponse]])
def get_popular_sounds(
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Lista las pistas de audio y música más utilizadas en la plataforma."""
    service = SearchService(db)
    popular = service.get_popular_sounds(limit=limit)
    return ApiResponse.success_response(data=popular, message="Sonidos populares obtenidos.")


@router.get("/hashtag/{hashtag_tag}", response_model=ApiResponse[List[VideoDetail]])
def get_videos_by_hashtag(
    hashtag_tag: str,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Consulta todos los videos asociados a una etiqueta hashtag específica."""
    service = SearchService(db)
    videos = service.get_videos_by_hashtag(hashtag=hashtag_tag, viewer=viewer, limit=limit, offset=offset)
    return ApiResponse.success_response(data=videos, message=f"Videos con #{hashtag_tag} obtenidos.")

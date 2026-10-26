from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, get_current_user_optional
from backend.core.response import ApiResponse
from backend.core.limiter import limiter
from backend.core.config import settings
from .schemas import (
    UserProfileUpdate, UserProfileView, SetParentalPinRequest,
    VerifyParentalPinRequest, ParentalSettingsUpdate, ParentalStatusResponse,
    PairChildRequest, ParentChildLinkResponse
)
from .service import UserService

router = APIRouter(prefix="/users", tags=["Usuarios y Control Parental"])


@router.get("/profile/{username}", response_model=ApiResponse[UserProfileView])
def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
    viewer: Optional[UserModel] = Depends(get_current_user_optional)
):
    """Consulta el perfil público de un usuario y sus estadísticas."""
    service = UserService(db)
    viewer_id = viewer.id if viewer else None
    profile = service.get_profile_by_username(username, viewer_id=viewer_id)
    return ApiResponse.success_response(data=profile, message="Perfil encontrado.")


@router.put("/profile", response_model=ApiResponse[UserProfileView])
def update_profile(
    req: UserProfileUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza los datos del perfil (nombre, bio, avatar, privacidad)."""
    service = UserService(db)
    updated = service.update_profile(current_user, req)
    return ApiResponse.success_response(data=updated, message="Perfil actualizado correctamente.")


@router.post("/{target_user_id}/follow", response_model=ApiResponse[dict])
def toggle_follow_user(
    target_user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sigue o deja de seguir a un usuario y genera notificación automática."""
    service = UserService(db)
    res = service.toggle_follow(current_user.id, target_user_id)
    return ApiResponse.success_response(data=res, message=res["message"])


# ------------------------------------------------------------------------------
# ENDPOINTS DE CONTROL PARENTAL Y VINCULACIÓN FAMILIAR
# ------------------------------------------------------------------------------
@router.post("/parental/pair-child", response_model=ApiResponse[ParentChildLinkResponse], status_code=status.HTTP_201_CREATED)
def pair_child_account(
    req: PairChildRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite a un padre/tutor vincular la cuenta de un menor para supervisión remota."""
    service = UserService(db)
    result = service.pair_child(current_user.id, req)
    return ApiResponse.success_response(data=result, message="Cuenta de menor vinculada con éxito.")


@router.get("/parental/children", response_model=ApiResponse[list[ParentChildLinkResponse]])
def get_linked_children(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la lista de cuentas de menores vinculadas al padre/tutor."""
    service = UserService(db)
    results = service.get_linked_children(current_user.id)
    return ApiResponse.success_response(data=results, message="Cuentas vinculadas obtenidas.")


@router.post("/parental/pin", response_model=ApiResponse[dict])
@limiter.limit(settings.RATE_LIMIT_PIN_PER_MINUTE)
def set_parental_pin(
    request: Request,
    req: SetParentalPinRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Establece o cambia el código PIN de 4-6 dígitos para control parental."""
    service = UserService(db)
    res = service.set_parental_pin(current_user.id, req)
    return ApiResponse.success_response(data=res, message=res["message"])


@router.post("/parental/pin/verify", response_model=ApiResponse[dict])
@limiter.limit(settings.RATE_LIMIT_PIN_PER_MINUTE)
def verify_parental_pin(
    request: Request,
    req: VerifyParentalPinRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Valida el código PIN parental para desbloquear funciones restringidas con protección anti-fuerza bruta."""
    service = UserService(db)
    res = service.verify_parental_pin(current_user.id, req)
    return ApiResponse.success_response(data=res, message=res["message"])


@router.get("/parental/settings", response_model=ApiResponse[ParentalStatusResponse])
def get_parental_settings(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la configuración actual de control parental de la cuenta."""
    service = UserService(db)
    config = service.get_or_create_parental_config(current_user.id)
    resp = ParentalStatusResponse(
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
    return ApiResponse.success_response(data=resp, message="Configuración obtenida.")


@router.put("/parental/settings", response_model=ApiResponse[ParentalStatusResponse])
def update_parental_settings(
    req: ParentalSettingsUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza parámetros parentales (límite de tiempo, toque de queda, modo restringido)."""
    service = UserService(db)
    updated = service.update_parental_settings(current_user.id, req)
    return ApiResponse.success_response(data=updated, message="Configuración parental guardada.")

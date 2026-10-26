from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, security_bearer
from backend.core.response import ApiResponse
from backend.core.limiter import limiter
from backend.core.config import settings
from .schemas import RegisterRequest, LoginRequest, RefreshTokenRequest, AuthResponseData, UserSummary
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=ApiResponse[AuthResponseData], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER_PER_MINUTE)
def register_user(request: Request, req: RegisterRequest, db: Session = Depends(get_db)):
    """Registra una nueva cuenta de usuario con validación de edad y control parental."""
    service = AuthService(db)
    result = service.register(req)
    return ApiResponse.success_response(data=result, message="Usuario registrado exitosamente.")


@router.post("/login", response_model=ApiResponse[AuthResponseData])
@limiter.limit(settings.RATE_LIMIT_LOGIN_PER_MINUTE)
def login_user(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    """Inicia sesión y genera tokens JWT de acceso y refresco."""
    service = AuthService(db)
    result = service.login(req)
    return ApiResponse.success_response(data=result, message="Sesión iniciada con éxito.")


@router.post("/refresh", response_model=ApiResponse[AuthResponseData])
@limiter.limit("20/minute")
def refresh_session(request: Request, req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Rota y genera nuevos tokens de acceso y refresco."""
    service = AuthService(db)
    result = service.refresh(req)
    return ApiResponse.success_response(data=result, message="Sesión renovada con éxito.")


@router.post("/logout", response_model=ApiResponse[dict])
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
):
    """Cierra la sesión del usuario revocando el token actual."""
    if credentials and credentials.credentials:
        service = AuthService(db)
        service.logout(credentials.credentials)
    return ApiResponse.success_response(data={"revoked": True}, message="Sesión cerrada correctamente.")


@router.get("/me", response_model=ApiResponse[UserSummary])
def get_current_profile(current_user: UserModel = Depends(get_current_user)):
    """Retorna los datos de la sesión del usuario actual autenticado."""
    from backend.reglas.parental_control import ParentalControlManager
    age = ParentalControlManager.calculate_user_age(current_user.birth_date)

    summary = UserSummary(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        birth_date=current_user.birth_date,
        role=current_user.role,
        account_type=current_user.account_type,
        is_minor=(age < 18),
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )
    return ApiResponse.success_response(data=summary, message="Perfil obtenido.")

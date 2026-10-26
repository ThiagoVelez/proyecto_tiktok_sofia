"""
Módulo de Seguridad, Criptografía y Control de Acceso (JWT, Hashing y Revocación).
Incluye soporte para Refresh Tokens, lista negra de tokens revocados (Token Blocklist)
y Control de Acceso Basado en Roles (RBAC).
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Callable
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, UserModel
from .redis_client import get_redis
from .logging import logger

security_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Genera un hash seguro bcrypt para la contraseña del usuario (soporta max 72 bytes)."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


from uuid import uuid4


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Access Token JWT firmado con corta vigencia para acceso a la API."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"jti": str(uuid4()), "exp": expire, "iat": now_utc, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Genera un Refresh Token JWT firmado con mayor vigencia para rotación de sesiones."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"jti": str(uuid4()), "exp": expire, "iat": now_utc, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida la firma y vigencia de un JWT."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def revoke_token(token: str, expire_seconds: Optional[int] = None) -> bool:
    """Registra el token en la lista de revocación (Token Blocklist) para cierre de sesión inmediato."""
    try:
        payload = decode_access_token(token)
        ttl = expire_seconds or (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        if payload and "exp" in payload:
            exp_ts = payload["exp"]
            now_ts = datetime.now(timezone.utc).timestamp()
            remaining = int(exp_ts - now_ts)
            if remaining > 0:
                ttl = remaining

        redis_client = get_redis()
        redis_client.set(f"revoked_token:{token}", "1", ex=ttl)
        return True
    except Exception as e:
        logger.error(f"Error al revocar token: {e}")
        return False


def is_token_revoked(token: str) -> bool:
    """Verifica si el token ha sido revocado activamente."""
    try:
        redis_client = get_redis()
        return bool(redis_client.exists(f"revoked_token:{token}"))
    except Exception:
        return False


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependencia FastAPI que autentica la solicitud mediante el Header Authorization: Bearer <token>.
    Valida la vigencia y rechaza tokens revocados en la lista negra.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión para acceder a este recurso.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha sido cerrada o el token fue revocado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado o cuenta inactiva.",
        )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[UserModel]:
    """Dependencia para endpoints públicos que pueden adaptarse si el usuario está autenticado."""
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    if is_token_revoked(token):
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user_id = payload.get("sub")
    return db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Control de Acceso Basado en Roles (RBAC).
    Verifica que el usuario actual tenga uno de los roles autorizados.
    """
    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}."
            )
        return current_user

    return role_checker

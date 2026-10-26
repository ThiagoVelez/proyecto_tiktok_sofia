"""
Gestor de Conexión a Redis con Soporte de Fallback en Memoria.
Proporciona pooling de conexiones, verificación de disponibilidad,
revocación de tokens, almacenamiento en caché y pub/sub para WebSockets.
"""

import time
from typing import Optional, Any
import redis
from .config import settings
from .logging import logger


class InMemoryCacheFallback:
    """Implementación de respaldo en memoria cuando Redis no está disponible."""

    def __init__(self):
        self._store = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        if key in self._expiry and self._expiry[key] < now:
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._store[key] = str(value)
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    def delete(self, key: str) -> bool:
        self._store.pop(key, None)
        self._expiry.pop(key, None)
        return True

    def exists(self, key: str) -> int:
        return 1 if self.get(key) is not None else 0

    def ping(self) -> bool:
        return True


class RedisManager:
    """Administrador centralizado de cliente Redis con reconexión protegida y fallback."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._fallback = InMemoryCacheFallback()
        self._is_connected = False
        self._last_attempt_time = 0.0
        self._retry_interval_seconds = 30.0

    def get_client(self) -> Any:
        if not settings.REDIS_ENABLED:
            return self._fallback

        now = time.time()
        if not self._is_connected:
            # Evitar pausas continuas de timeout si Redis no está activo localmente
            if now - self._last_attempt_time < self._retry_interval_seconds:
                return self._fallback

            self._last_attempt_time = now
            try:
                candidate = redis.Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=0.3,
                    socket_timeout=0.3
                )
                candidate.ping()
                self._client = candidate
                self._is_connected = True
                logger.info("Conexión con Redis establecida exitosamente.", extra={"extra_data": {"host": settings.REDIS_HOST}})
                return self._client
            except Exception:
                self._client = None
                self._is_connected = False
                return self._fallback

        return self._client or self._fallback

    def ping(self) -> bool:
        """Verifica si el servicio Redis remoto responde activamente."""
        if not settings.REDIS_ENABLED or not self._is_connected or self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            self._is_connected = False
            self._client = None
            return False

    @property
    def is_healthy(self) -> bool:
        return self.ping()


redis_manager = RedisManager()


def get_redis():
    """Retorna el cliente Redis activo o el fallback en memoria."""
    return redis_manager.get_client()

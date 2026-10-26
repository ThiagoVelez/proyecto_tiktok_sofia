"""
Módulo de Reglas: Control Parental y Protección a Menores
Proyecto Sofía - Plataforma de Videos Cortos (TikTok-like)

Este módulo implementa las reglas de negocio para:
1. Código PIN parental (cifrado, validación de intentos y bloqueo temporal)
2. Límites de tiempo diario de pantalla (Daily Screen Time Limits)
3. Horario de toque de queda / descanso nocturno (Curfew Enforcement)
4. Modo Restringido (Restricted Mode) para audiencia menor de edad
5. Restricciones de comunicación y mensajes directos para menores
6. Reglas de vinculación entre cuentas de padres y tutores
"""

import hashlib
import hmac
import secrets
from datetime import datetime, time, date, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ParentalStatus(str, Enum):
    ALLOWED = "allowed"
    TIME_EXCEEDED = "time_exceeded"
    CURFEW_ACTIVE = "curfew_active"
    RESTRICTED_CONTENT = "restricted_content"
    PIN_REQUIRED = "pin_required"
    PIN_LOCKED = "pin_locked"


@dataclass
class ScreenTimeEvaluation:
    is_allowed: bool
    status: ParentalStatus
    minutes_consumed: int
    daily_limit: int
    minutes_remaining: int
    curfew_active: bool
    message: str


class ParentalControlManager:
    """
    Gestor de reglas de Control Parental y protección infantil.
    Diseñado siguiendo los principios SOLID: Responsabilidad única y alta cohesión.
    """

    MAX_PIN_ATTEMPTS: int = 3
    LOCKOUT_DURATION_MINUTES: int = 15
    DEFAULT_DAILY_LIMIT_MINUTES: int = 120

    @staticmethod
    def hash_parental_pin(pin: str, salt: Optional[str] = None) -> str:
        """
        Cifra un código PIN parental de 4 a 6 dígitos con salting criptográfico.
        Formato devuelto: 'salt$hash'
        """
        if not pin.isdigit() or len(pin) not in (4, 6):
            raise ValueError("El código PIN parental debe tener exactamente 4 o 6 dígitos numéricos.")

        if not salt:
            salt = secrets.token_hex(16)

        derived = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=pin.encode("utf-8"),
            salt=salt.encode("utf-8"),
            iterations=100_000
        ).hex()

        return f"{salt}${derived}"

    @classmethod
    def verify_parental_pin(
        cls,
        stored_hash: Optional[str],
        input_pin: str,
        failed_attempts: int = 0,
        locked_until: Optional[datetime] = None
    ) -> Tuple[bool, int, Optional[datetime], str]:
        """
        Verifica un código PIN parental ingresado.
        Retorna: (es_valido, nuevos_intentos_fallidos, bloqueado_hasta, mensaje)
        """
        now = datetime.now(timezone.utc)

        # Verificar si el PIN se encuentra bloqueado por demasiados intentos
        if locked_until:
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if now < locked_until:
                remaining_mins = max(1, int((locked_until - now).total_seconds() // 60))
                return False, failed_attempts, locked_until, f"PIN temporalmente bloqueado. Intenta de nuevo en {remaining_mins} minutos."

        if not stored_hash or "$" not in stored_hash:
            return False, failed_attempts, None, "No hay código PIN parental configurado."

        salt, expected_hash = stored_hash.split("$", 1)
        calculated = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=input_pin.encode("utf-8"),
            salt=salt.encode("utf-8"),
            iterations=100_000
        ).hex()

        if hmac.compare_digest(calculated, expected_hash):
            # PIN Correcto: reiniciar intentos fallidos
            return True, 0, None, "Código PIN parental verificado con éxito."
        else:
            new_attempts = failed_attempts + 1
            if new_attempts >= cls.MAX_PIN_ATTEMPTS:
                new_lockout = now + timedelta(minutes=cls.LOCKOUT_DURATION_MINUTES)
                return False, new_attempts, new_lockout, f"Demasiados intentos fallidos. PIN bloqueado por {cls.LOCKOUT_DURATION_MINUTES} minutos."
            else:
                remaining_tries = cls.MAX_PIN_ATTEMPTS - new_attempts
                return False, new_attempts, None, f"PIN incorrecto. Te quedan {remaining_tries} intento(s)."


    @staticmethod
    def is_curfew_active(
        curfew_start: Optional[time],
        curfew_end: Optional[time],
        current_time: Optional[time] = None
    ) -> bool:
        """
        Determina si la hora actual cae dentro del periodo de descanso/toque de queda nocturno.
        Por ejemplo: curfew de 22:00 a 06:00.
        """
        if not curfew_start or not curfew_end:
            return False

        if current_time is None:
            current_time = datetime.now().time()

        if curfew_start <= curfew_end:
            # Rango en el mismo día (ej. 14:00 a 16:00)
            return curfew_start <= current_time <= curfew_end
        else:
            # Rango que cruza la medianoche (ej. 22:00 a 06:00)
            return current_time >= curfew_start or current_time <= curfew_end

    @classmethod
    def evaluate_screen_time(
        cls,
        daily_limit_minutes: int,
        minutes_consumed_today: int,
        curfew_start: Optional[time] = None,
        curfew_end: Optional[time] = None,
        current_time: Optional[time] = None
    ) -> ScreenTimeEvaluation:
        """
        Evalúa si el usuario (especialmente menores de edad) tiene permiso de seguir viendo videos hoy.
        """
        curfew_active = cls.is_curfew_active(curfew_start, curfew_end, current_time)
        if curfew_active:
            return ScreenTimeEvaluation(
                is_allowed=False,
                status=ParentalStatus.CURFEW_ACTIVE,
                minutes_consumed=minutes_consumed_today,
                daily_limit=daily_limit_minutes,
                minutes_remaining=0,
                curfew_active=True,
                message="Horario de descanso activo. El uso de la plataforma está pausado hasta la mañana."
            )

        limit = daily_limit_minutes if daily_limit_minutes > 0 else cls.DEFAULT_DAILY_LIMIT_MINUTES
        remaining = max(0, limit - minutes_consumed_today)

        if minutes_consumed_today >= limit:
            return ScreenTimeEvaluation(
                is_allowed=False,
                status=ParentalStatus.TIME_EXCEEDED,
                minutes_consumed=minutes_consumed_today,
                daily_limit=limit,
                minutes_remaining=0,
                curfew_active=False,
                message=f"Has alcanzado el límite diario de {limit} minutos configurado por control parental."
            )

        return ScreenTimeEvaluation(
            is_allowed=True,
            status=ParentalStatus.ALLOWED,
            minutes_consumed=minutes_consumed_today,
            daily_limit=limit,
            minutes_remaining=remaining,
            curfew_active=False,
            message=f"Uso permitido. Te quedan {remaining} minutos hoy."
        )

    @staticmethod
    def calculate_user_age(birth_date: date) -> int:
        """Calcula la edad exacta de un usuario a partir de su fecha de nacimiento."""
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    @classmethod
    def can_access_video_by_age_and_mode(
        cls,
        user_age: int,
        is_minor_account: bool,
        restricted_mode_enabled: bool,
        video_rating: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Evalúa si un video es apto para un usuario en base a su edad y el modo restringido.
        Clasificaciones de video: 'all_ages', 'teen', 'mature', 'restricted'.
        """
        rating = video_rating.lower()

        # Si el modo restringido está activo, solo se permiten videos para todo público
        if restricted_mode_enabled and rating in ("mature", "restricted"):
            return False, "Este contenido no está disponible porque el Modo Restringido de Control Parental está activo."

        # Menores de 13 años no deben ver contenido teen ni mature
        if user_age < 13 and rating != "all_ages":
            return False, "Este video no es apto para menores de 13 años."

        # Menores de 18 años no pueden ver contenido clasificado como mature o restricted
        if (user_age < 18 or is_minor_account) and rating in ("mature", "restricted"):
            return False, "Este video contiene material clasificado para mayores de edad."

        return True, None

    @staticmethod
    def can_send_direct_message(
        sender_age: int,
        receiver_age: int,
        receiver_blocks_dms: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Regla de seguridad infantil: protege a menores de contacto por adultos desconocidos.
        """
        if receiver_age < 16 and sender_age >= 18:
            return False, "Por seguridad de la comunidad, las cuentas de adultos no pueden enviar mensajes privados directos a menores de 16 años."

        if receiver_age < 18 and receiver_blocks_dms:
            return False, "La cuenta del destinatario tiene activada la protección parental contra mensajes de desconocidos."

        return True, None

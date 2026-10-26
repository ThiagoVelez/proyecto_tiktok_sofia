"""
Módulo de Registro Estructurado (Structured Logging) y Trazabilidad.
Proporciona formato JSON en producción, identificador único de correlación (Request-ID)
y cumplimiento estricto de la política de cero emojis.
"""

import sys
import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class StructuredJsonFormatter(logging.Formatter):
    """Formateador de logs en formato JSON estandarizado para observabilidad centralizada."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        req_id = correlation_id_ctx.get()
        if req_id:
            log_entry["correlation_id"] = req_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_format: bool = True) -> logging.Logger:
    """Configura el registrador raíz con salida a stdout y formato estructurado."""
    root_logger = logging.getLogger("sofia_backend")
    root_logger.setLevel(level.upper())

    # Evitar duplicación de manejadores
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if json_format:
            handler.setFormatter(StructuredJsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
            )
        root_logger.addHandler(handler)

    return root_logger


logger = setup_logging()

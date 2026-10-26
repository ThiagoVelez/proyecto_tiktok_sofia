# ==============================================================================
# PROYECTO SOFÍA - DOCKERFILE MULTI-STAGE DE PRODUCCIÓN (FASTAPI BACKEND)
# ==============================================================================

# Etapa 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Entorno virtual aislado para evitar advertencias de pip y asegurar portabilidad
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 2: Imagen Final Runtime
FROM python:3.12-slim AS runtime

WORKDIR /app

# Instalar FFmpeg para procesamiento de video y curl para comprobaciones de estado
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias compiladas en entorno virtual accesible para cualquier usuario
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Variables de entorno de ejecución Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Crear usuario sin privilegios para mitigar riesgos de seguridad
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/backend/uploads /app/uploads && \
    chown -R appuser:appuser /app

# Copiar código fuente
COPY --chown=appuser:appuser . /app

USER appuser

EXPOSE 8000

# Healthcheck de contenedor nativo compatible con puerto dinámico en la nube
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]

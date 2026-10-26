"""
Capa de Abstracción de Almacenamiento de Archivos Multimedia (Storage Service).
Soporta almacenamiento Local y Object Storage compatible con S3 (AWS S3, MinIO, Cloudflare R2).
Incluye validación estricta de firmas binarias (Magic Bytes) para neutralizar cargas maliciosas.
"""

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Optional
from uuid import uuid4
from fastapi import HTTPException, status, UploadFile

from .config import settings
from .logging import logger

# Firmas de bytes mágicos permitidas
MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xFF\xD8\xFF"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],  # Con 'WEBP' en byte 8..12
    "video/mp4": [b"ftyp"],   # En byte 4..8
    "video/webm": [b"\x1a\x45\xdf\xa3"],
    "video/quicktime": [b"moov", b"ftypqt"],
}


def validate_file_magic_bytes(header_bytes: bytes, expected_type: str) -> bool:
    """
    Inspecciona los primeros bytes del archivo para certificar que el contenido
    coincide con el tipo multimedia declarado, evitando ataques de archivo políglota.
    """
    if len(header_bytes) < 12:
        return False

    if expected_type == "image":
        # PNG
        if header_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        # JPEG
        if header_bytes.startswith(b"\xFF\xD8\xFF"):
            return True
        # WebP: Comienza con 'RIFF' y en offset 8 tiene 'WEBP'
        if header_bytes.startswith(b"RIFF") and header_bytes[8:12] == b"WEBP":
            return True
        return False

    if expected_type == "video":
        # WebM / MKV
        if header_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            return True
        # MP4 / MOV (Común: bytes 4..8 son 'ftyp')
        if len(header_bytes) >= 8 and header_bytes[4:8] in (b"ftyp", b"moov"):
            return True
        # QuickTime MOV
        if b"moov" in header_bytes[:32] or b"ftyp" in header_bytes[:32]:
            return True
        return False

    return False


class BaseStorageBackend(ABC):
    """Interfaz abstracta del proveedor de almacenamiento."""

    @abstractmethod
    async def save_file(self, file: UploadFile, subdir: str, safe_filename: str) -> Tuple[str, int]:
        """Guarda el archivo y retorna la URL pública/relativa y el tamaño en bytes."""
        pass

    @abstractmethod
    def delete_file(self, file_path_or_key: str) -> bool:
        """Elimina el archivo del almacenamiento."""
        pass


class LocalStorageBackend(BaseStorageBackend):
    """Almacenamiento en sistema de archivos local."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    async def save_file(self, file: UploadFile, subdir: str, safe_filename: str) -> Tuple[str, int]:
        target_dir = self.base_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_path = target_dir / safe_filename

        max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
        total_bytes = 0

        # Leer primer bloque para validación de magic bytes
        first_chunk = await file.read(1024)
        if not first_chunk:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo subido está vacío.")

        media_category = "video" if subdir in ("videos", "stories") else "image"
        # Verificar extensión y concordancia con magic bytes
        if not validate_file_magic_bytes(first_chunk, media_category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firma binaria de archivo no válida o contenido corrupto/malicioso."
            )

        with open(dest_path, "wb") as buffer:
            buffer.write(first_chunk)
            total_bytes += len(first_chunk)

            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > max_size_bytes:
                    buffer.close()
                    dest_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"El archivo excede el tamaño máximo permitido ({settings.MAX_VIDEO_SIZE_MB}MB)."
                    )
                buffer.write(chunk)

        url = f"/uploads/{subdir}/{safe_filename}"
        return url, total_bytes

    def delete_file(self, file_path_or_key: str) -> bool:
        rel = file_path_or_key.lstrip("/").replace("uploads/", "")
        p = self.base_dir / rel
        if p.exists() and p.is_file():
            p.unlink()
            return True
        return False


class S3StorageBackend(BaseStorageBackend):
    """Almacenamiento en S3 / MinIO Object Storage."""

    def __init__(self):
        import boto3
        from botocore.config import Config

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4")
        )
        self.bucket = settings.S3_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
                logger.info(f"Bucket S3 '{self.bucket}' creado satisfactoriamente.")
            except Exception as e:
                logger.warning(f"No se pudo crear automáticamente el bucket S3: {e}")

    async def save_file(self, file: UploadFile, subdir: str, safe_filename: str) -> Tuple[str, int]:
        s3_key = f"{subdir}/{safe_filename}"
        first_chunk = await file.read(1024)
        if not first_chunk:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo subido está vacío.")

        media_category = "video" if subdir in ("videos", "stories") else "image"
        if not validate_file_magic_bytes(first_chunk, media_category):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firma binaria de archivo no válida o contenido corrupto/malicioso."
            )

        content = first_chunk + await file.read()
        content_type = file.content_type or ("video/mp4" if media_category == "video" else "image/jpeg")

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=content,
            ContentType=content_type
        )

        if settings.S3_PUBLIC_URL:
            url = f"{settings.S3_PUBLIC_URL.rstrip('/')}/{self.bucket}/{s3_key}"
        elif settings.S3_ENDPOINT_URL:
            url = f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{self.bucket}/{s3_key}"
        else:
            url = f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"

        return url, len(content)

    def delete_file(self, file_path_or_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_path_or_key)
            return True
        except Exception:
            return False


def get_storage_backend() -> BaseStorageBackend:
    """Inyección de dependencias para el backend de almacenamiento configurado."""
    if settings.STORAGE_BACKEND == "s3":
        try:
            return S3StorageBackend()
        except Exception as e:
            logger.warning(f"Error inicializando backend S3, usando almacenamiento local: {e}")
            return LocalStorageBackend(settings.UPLOAD_DIR)
    return LocalStorageBackend(settings.UPLOAD_DIR)

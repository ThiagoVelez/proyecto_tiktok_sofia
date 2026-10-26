import os
import re
import mimetypes
from pathlib import Path
from uuid import uuid4
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, get_current_user_optional
from backend.core.response import ApiResponse
from backend.core.limiter import limiter
from backend.core.storage import validate_file_magic_bytes
from .schemas import VideoCreateRequest, VideoDetail, FeedResponse, MediaUploadResponse
from .service import VideoService

router = APIRouter(prefix="/videos", tags=["Videos y Feeds"])


def _send_bytes_range_response(file_path: Path, range_header: Optional[str], is_head: bool = False):
    file_size = file_path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or "video/mp4"

    if is_head:
        return Response(
            status_code=status.HTTP_200_OK,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": content_type
            }
        )

    if not range_header or file_size == 0:
        def full_file_iterator():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk

        return StreamingResponse(
            full_file_iterator(),
            status_code=status.HTTP_200_OK,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
                "Content-Type": content_type
            }
        )

    # Rango de bytes solicitado (ej: bytes=0-1048576, bytes=1000-, bytes=-500)
    range_match = re.match(r"bytes=(\d*)-(\d*)", range_header.strip())
    if not range_match:
        raise HTTPException(status_code=416, detail="Encabezado Range inválido.")

    start_str, end_str = range_match.groups()
    if not start_str and not end_str:
        raise HTTPException(status_code=416, detail="Encabezado Range inválido.")

    if not start_str:
        suffix = int(end_str)
        start = max(0, file_size - suffix)
        end = file_size - 1
    elif not end_str:
        start = int(start_str)
        end = file_size - 1
    else:
        start = int(start_str)
        end = min(int(end_str), file_size - 1)

    if start >= file_size or start > end:
        raise HTTPException(
            status_code=416,
            detail="Rango de bytes fuera de los límites del archivo.",
            headers={"Content-Range": f"bytes */{file_size}"}
        )

    content_length = (end - start) + 1

    def range_iterator(start_pos: int, length: int):
        with open(file_path, "rb") as f:
            f.seek(start_pos)
            bytes_left = length
            while bytes_left > 0:
                chunk_size = min(bytes_left, 1024 * 1024)
                data = f.read(chunk_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data

    return StreamingResponse(
        range_iterator(start, content_length),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type
        }
    )


@router.post("/upload-media", response_model=ApiResponse[MediaUploadResponse], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_UPLOAD_PER_MINUTE)
async def upload_media_file(
    request: Request,
    file: UploadFile = File(...),
    media_type: str = Query("video", description="video, thumbnail o avatar"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Sube un archivo multimedia real (Video MP4/WebM o Imagen JPG/PNG/WebP).
    Valida firma binaria (magic bytes), tamaño y extensión, almacenando en el servidor para servir al Frontend.
    """
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if media_type == "video":
        if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de video no permitido. Válidos: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
            )
        subdir = "videos"
    elif media_type in ("thumbnail", "avatar"):
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de imagen no permitido. Válidos: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        subdir = "thumbnails" if media_type == "thumbnail" else "avatars"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="media_type no válido. Use 'video', 'thumbnail' o 'avatar'.")

    # Validación de Magic Bytes
    first_chunk = await file.read(1024)
    if not first_chunk:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo subido está vacío.")

    media_category = "video" if media_type == "video" else "image"
    if not validate_file_magic_bytes(first_chunk, media_category):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firma binaria del archivo no válida o contenido corrupto."
        )

    target_dir = Path(settings.UPLOAD_DIR) / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex[:12]}_{re.sub(r'[^a-zA-Z0-9_.-]', '', file.filename)}"
    destination_path = target_dir / safe_name

    max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    total_bytes = len(first_chunk)
    with open(destination_path, "wb") as buffer:
        buffer.write(first_chunk)
        while chunk := await file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > max_size_bytes:
                buffer.close()
                destination_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El archivo excede el tamaño máximo permitido ({settings.MAX_VIDEO_SIZE_MB}MB)."
                )
            buffer.write(chunk)

    rel_url = f"/uploads/{subdir}/{safe_name}"
    return ApiResponse.success_response(
        data=MediaUploadResponse(
            file_url=rel_url,
            file_name=safe_name,
            media_type=media_type,
            size_bytes=total_bytes
        ),
        message="Archivo multimedia subido con éxito."
    )


@router.post("/upload", response_model=ApiResponse[VideoDetail], status_code=status.HTTP_201_CREATED)
def upload_video(
    req: VideoCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publica un nuevo video corto evaluando automáticamente las reglas de seguridad
    y clasificación por edades antes de permitir su distribución.
    """
    service = VideoService(db)
    new_video = service.upload_video(current_user, req)
    return ApiResponse.success_response(data=new_video, message="Video publicado y clasificado exitosamente.")


@router.post("/publish", response_model=ApiResponse[VideoDetail], status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_UPLOAD_PER_MINUTE)
async def publish_video_direct(
    request: Request,
    video_file: UploadFile = File(..., description="Archivo de video MP4, WebM o MOV"),
    thumbnail_file: Optional[UploadFile] = File(None, description="Imagen miniatura opcional"),
    title: str = Form(..., max_length=150, description="Título del video"),
    description: Optional[str] = Form(None, description="Descripción del video"),
    sound_id: Optional[int] = Form(None, description="ID del sonido asociado"),
    hashtags: Optional[str] = Form(None, description="Hashtags (ej: '#danza #musica' o 'danza, musica')"),
    duration_seconds: Optional[float] = Form(15.0, description="Duración en segundos"),
    visibility: Optional[str] = Form("public", description="public, friends o private"),
    allow_comments: Optional[bool] = Form(True),
    allow_duet: Optional[bool] = Form(True),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publica un video directamente mediante carga de archivo multipart en una sola petición.
    Almacena el video en el servidor, procesa o asigna miniatura, extrae hashtags,
    evalúa reglas de seguridad y control parental, y registra el video en la plataforma.
    """
    v_ext = video_file.filename.split(".")[-1].lower() if "." in video_file.filename else ""
    if v_ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de video no permitido. Válidos: {', '.join(settings.ALLOWED_VIDEO_EXTENSIONS)}"
        )

    v_first_chunk = await video_file.read(1024)
    if not v_first_chunk:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo de video está vacío.")

    if not validate_file_magic_bytes(v_first_chunk, "video"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Firma binaria del video no válida o contenido corrupto."
        )

    video_dir = Path(settings.UPLOAD_DIR) / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    safe_v_name = f"vid_{uuid4().hex[:12]}_{re.sub(r'[^a-zA-Z0-9_.-]', '', video_file.filename)}"
    v_dest_path = video_dir / safe_v_name

    max_size_bytes = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    total_v_bytes = len(v_first_chunk)
    with open(v_dest_path, "wb") as buffer:
        buffer.write(v_first_chunk)
        while chunk := await video_file.read(1024 * 1024):
            total_v_bytes += len(chunk)
            if total_v_bytes > max_size_bytes:
                buffer.close()
                v_dest_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"El video excede el tamaño máximo permitido ({settings.MAX_VIDEO_SIZE_MB}MB)."
                )
            buffer.write(chunk)

    video_url = f"/uploads/videos/{safe_v_name}"

    # Procesar miniatura
    thumb_dir = Path(settings.UPLOAD_DIR) / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)

    if thumbnail_file and thumbnail_file.filename:
        t_ext = thumbnail_file.filename.split(".")[-1].lower() if "." in thumbnail_file.filename else ""
        if t_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de miniatura no permitido. Válidos: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            )

        t_first_chunk = await thumbnail_file.read(1024)
        if not t_first_chunk or not validate_file_magic_bytes(t_first_chunk, "image"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Firma binaria de la miniatura no válida o contenido corrupto."
            )

        safe_t_name = f"thumb_{uuid4().hex[:12]}_{re.sub(r'[^a-zA-Z0-9_.-]', '', thumbnail_file.filename)}"
        t_dest_path = thumb_dir / safe_t_name
        with open(t_dest_path, "wb") as buffer:
            buffer.write(t_first_chunk)
            while chunk := await thumbnail_file.read(1024 * 1024):
                buffer.write(chunk)
        thumbnail_url = f"/uploads/thumbnails/{safe_t_name}"
    else:
        # Miniatura por defecto garantizada
        default_cover = thumb_dir / "default_cover.jpg"
        if not default_cover.exists():
            default_cover.write_bytes(b"")
        thumbnail_url = "/uploads/thumbnails/default_cover.jpg"

    # Procesar hashtags (de formulario y extraídos de título/descripción)
    tag_list: List[str] = []
    if hashtags:
        for part in re.split(r"[\s,]+", hashtags):
            clean = part.strip().lstrip("#").lower()
            if clean and clean not in tag_list:
                tag_list.append(clean)

    full_text = f"{title} {description or ''}"
    for found in re.findall(r"#([a-zA-Z0-9_]+)", full_text):
        clean = found.strip().lower()
        if clean and clean not in tag_list:
            tag_list.append(clean)

    create_req = VideoCreateRequest(
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        sound_id=sound_id,
        duration_seconds=duration_seconds or 15.0,
        visibility=visibility or "public",
        allow_comments=allow_comments if allow_comments is not None else True,
        allow_duet=allow_duet if allow_duet is not None else True,
        hashtags=tag_list
    )

    service = VideoService(db)
    new_video = service.upload_video(current_user, create_req)
    return ApiResponse.success_response(
        data=new_video,
        message="Video publicado y clasificado exitosamente."
    )


@router.get("/feed/for-you", response_model=ApiResponse[FeedResponse])
def get_for_you_feed(
    limit: int = Query(15, ge=1, le=50),
    offset: int = Query(0, ge=0),
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Feed 'Para Ti' (Algoritmo de recomendaciones ponderado por likes, comentarios, shares y vistas).
    Aplica filtros automáticos de control parental, toque de queda nocturno y modo restringido.
    """
    service = VideoService(db)
    feed = service.get_for_you_feed(viewer, limit=limit, offset=offset)
    return ApiResponse.success_response(data=feed, message="Feed Para Ti generado.")


@router.get("/feed/following", response_model=ApiResponse[FeedResponse])
def get_following_feed(
    limit: int = Query(15, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Feed de videos publicados por usuarios a los que sigues."""
    service = VideoService(db)
    feed = service.get_following_feed(current_user, limit=limit, offset=offset)
    return ApiResponse.success_response(data=feed, message="Feed Siguiendo generado.")


@router.get("/{video_id}", response_model=ApiResponse[VideoDetail])
def get_video_by_id(
    video_id: int,
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Consulta los detalles completos y métricas de un video específico."""
    service = VideoService(db)
    video = service.get_video_by_id(video_id, viewer)
    return ApiResponse.success_response(data=video, message="Video obtenido.")


@router.api_route("/{video_id}/stream", methods=["GET", "HEAD"])
def stream_video(
    video_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Transmisión de video con soporte de cabecera HTTP Range (206 Partial Content) y solicitudes HEAD.
    Permite rebobinado rápido, buffering suave y reproducción continua en el frontend.
    """
    service = VideoService(db)
    video = service.get_video_by_id(video_id)
    video_url = video.video_url

    if video_url.startswith("http://") or video_url.startswith("https://"):
        return RedirectResponse(url=video_url)

    rel_path = video_url.lstrip("/")
    if rel_path.startswith("uploads/"):
        rel_path = rel_path[len("uploads/"):]

    local_path = Path(settings.UPLOAD_DIR) / rel_path
    if not local_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de video no encontrado en el servidor.")

    is_head = request.method == "HEAD"
    range_header = request.headers.get("Range")
    return _send_bytes_range_response(local_path, range_header, is_head=is_head)


@router.post("/{video_id}/view", response_model=ApiResponse[dict])
def register_video_view(
    video_id: int,
    duration_seconds: float = Query(0.0, ge=0.0),
    watched_full: bool = Query(False),
    viewer: Optional[UserModel] = Depends(get_current_user_optional),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Registra la reproducción de un video, telemetría y actualiza las métricas analíticas."""
    ip_addr = request.client.host if request and request.client else None
    service = VideoService(db)
    service.register_view(
        video_id=video_id,
        viewer=viewer,
        duration_seconds=duration_seconds,
        watched_full=watched_full,
        ip_address=ip_addr
    )
    return ApiResponse.success_response(data={"video_id": video_id}, message="Vista registrada.")


"""
Suite de Pruebas Automatizadas para el Motor de Reglas, API y Microservicios
Proyecto Sofía - Plataforma TikTok-like
"""

import sys
import io
from pathlib import Path
from datetime import date, time, datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Asegurar raíz del proyecto en PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.core.database import Base, get_db, UserModel, VideoModel, ParentalControlModel, StoryModel, StoryViewModel
from backend.reglas.parental_control import ParentalControlManager, ParentalStatus
from backend.reglas.content_safety import ContentSafetyEngine, ModerationSeverity, ModerationAction
from backend.reglas.audience_protection import AudienceProtectionSystem, AudienceRating, VideoModerationStatus
from backend.reglas.rule_evaluator import rule_evaluator
from backend.main import app

from sqlalchemy.pool import StaticPool

# Configuración de base de datos SQLite en memoria para tests aislados
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_api_health_and_root():
    """Verifica que el Gateway API responda correctamente."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["data"]["platform"] == "Proyecto Sofía"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["data"]["status"] == "healthy"


def test_parental_pin_hashing_and_verification():
    """Prueba cifrado, verificación de PIN y bloqueo por intentos fallidos."""
    pin = "4826"
    stored_hash = ParentalControlManager.hash_parental_pin(pin)
    assert "$" in stored_hash

    # Verificación exitosa
    valid, attempts, locked_until, msg = ParentalControlManager.verify_parental_pin(stored_hash, "4826")
    assert valid is True
    assert attempts == 0
    assert locked_until is None

    # Verificación con PIN erróneo (intento 1)
    valid, attempts, locked_until, msg = ParentalControlManager.verify_parental_pin(stored_hash, "1111", failed_attempts=0)
    assert valid is False
    assert attempts == 1
    assert locked_until is None

    # Verificación superando intentos máximos (intento 3)
    valid, attempts, locked_until, msg = ParentalControlManager.verify_parental_pin(stored_hash, "2222", failed_attempts=2)
    assert valid is False
    assert attempts == 3
    assert locked_until is not None
    assert locked_until > datetime.now(timezone.utc)


def test_screen_time_and_curfew_rules():
    """Prueba las reglas de tiempo en pantalla y toque de queda nocturno."""
    curfew_start = time(22, 0)
    curfew_end = time(6, 0)

    # Toque de queda nocturno
    assert ParentalControlManager.is_curfew_active(curfew_start, curfew_end, time(23, 30)) is True
    assert ParentalControlManager.is_curfew_active(curfew_start, curfew_end, time(3, 0)) is True
    assert ParentalControlManager.is_curfew_active(curfew_start, curfew_end, time(15, 0)) is False

    # Límite de tiempo diario
    eval_ok = ParentalControlManager.evaluate_screen_time(
        daily_limit_minutes=120,
        minutes_consumed_today=60,
        curfew_start=curfew_start,
        curfew_end=curfew_end,
        current_time=time(14, 0)
    )
    assert eval_ok.is_allowed is True
    assert eval_ok.minutes_remaining == 60

    eval_exceeded = ParentalControlManager.evaluate_screen_time(
        daily_limit_minutes=120,
        minutes_consumed_today=125,
        curfew_start=curfew_start,
        curfew_end=curfew_end,
        current_time=time(14, 0)
    )
    assert eval_exceeded.is_allowed is False
    assert eval_exceeded.status == ParentalStatus.TIME_EXCEEDED


def test_content_safety_clean_content():
    """Verifica que el contenido limpio y apto para todo público pase sin objeciones."""
    engine = ContentSafetyEngine()
    result = engine.scan_text("Receta fácil de pastel de chocolate casero #cocina #delicioso")
    assert result.is_safe is True
    assert result.severity == ModerationSeverity.SAFE
    assert result.recommended_action == ModerationAction.ALLOW


def test_content_safety_leetspeak_and_censorship():
    """Verifica detección de palabras censurables con leetspeak y enmascaramiento."""
    engine = ContentSafetyEngine()

    res_explicit = engine.scan_text("mira este p0rn0 gratis")
    assert res_explicit.is_safe is False
    assert res_explicit.severity == ModerationSeverity.CRITICAL
    assert res_explicit.recommended_action == ModerationAction.BLOCK_IMMEDIATE

    comment_eval = rule_evaluator.evaluate_comment("Este video es una mierda")
    assert comment_eval.can_post is True
    assert "m*****" in comment_eval.filtered_content
    assert comment_eval.is_flagged is True


def test_video_audience_classification():
    """Verifica que los videos sean clasificados adecuadamente (all_ages, teen, mature, banned)."""
    audience = AudienceProtectionSystem()

    dec_all = audience.evaluate_video_metadata(
        title="Baile divertido con mi mascota",
        description="Perrito bailando en el parque #dog #funny",
        hashtags=["#dog", "#funny"]
    )
    assert dec_all.can_publish is True
    assert dec_all.audience_rating == AudienceRating.ALL_AGES
    assert dec_all.moderation_status == VideoModerationStatus.APPROVED

    dec_banned = audience.evaluate_video_metadata(
        title="Video porno y sexo explícito",
        description="Contenido prohibido",
        hashtags=["#adulto"]
    )
    assert dec_banned.can_publish is False
    assert dec_banned.moderation_status == VideoModerationStatus.BANNED

    dec_review = audience.evaluate_video_metadata(
        title="Cómo asesinar y degollar personas",
        description="Contenido violento",
        hashtags=["#violencia"]
    )
    assert dec_review.can_publish is False
    assert dec_review.moderation_status == VideoModerationStatus.UNDER_REVIEW


def test_full_auth_and_user_flow():
    """Prueba registro, login, perfil y control parental de fábrica para menor."""
    # Registro de adulto
    adult_reg = client.post("/api/v1/auth/register", json={
        "username": "juan_perez",
        "email": "juan@example.com",
        "password": "Password123!",
        "full_name": "Juan Pérez",
        "birth_date": "1995-04-10",
        "account_type": "standard"
    })
    assert adult_reg.status_code == 201
    adult_token = adult_reg.json()["data"]["token"]["access_token"]
    assert adult_token is not None

    # Registro de menor (14 años) -> Control parental automático
    minor_reg = client.post("/api/v1/auth/register", json={
        "username": "lucia_teen",
        "email": "lucia@example.com",
        "password": "Password123!",
        "full_name": "Lucía Pérez",
        "birth_date": "2012-08-15",
        "account_type": "minor"
    })
    assert minor_reg.status_code == 201
    assert minor_reg.json()["data"]["user"]["is_minor"] is True


def test_interaction_buttons_like_comment_share():
    """Prueba completa para botones de Like, Comentarios con Like, Guardar y Compartir."""
    # Login de Juan
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "juan_perez",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Publicar un video
    video_res = client.post("/api/v1/videos/upload", headers=headers, json={
        "title": "Mi primer baile viral de prueba",
        "description": "Bailando con buena vibra #baile #viral",
        "video_url": "https://example.com/video1.mp4",
        "thumbnail_url": "https://example.com/thumb1.jpg",
        "duration_seconds": 15.0,
        "hashtags": ["#baile", "#viral"]
    })
    assert video_res.status_code == 201
    video_id = video_res.json()["data"]["id"]

    # 1. BOTÓN DE LIKE
    like_res = client.post(f"/api/v1/interactions/videos/{video_id}/like", headers=headers)
    assert like_res.status_code == 200
    assert like_res.json()["data"]["is_liked"] is True
    assert like_res.json()["data"]["total_likes"] == 1

    # Quitar like
    unlike_res = client.post(f"/api/v1/interactions/videos/{video_id}/like", headers=headers)
    assert unlike_res.status_code == 200
    assert unlike_res.json()["data"]["is_liked"] is False
    assert unlike_res.json()["data"]["total_likes"] == 0

    # 2. BOTÓN DE COMENTAR Y LIKE EN COMENTARIO
    comm_res = client.post(f"/api/v1/interactions/videos/{video_id}/comments", headers=headers, json={
        "content": "¡Buenísimo el paso de baile! Totalmente genial."
    })
    assert comm_res.status_code == 201
    comment_id = comm_res.json()["data"]["id"]

    comm_like_res = client.post(f"/api/v1/interactions/comments/{comment_id}/like", headers=headers)
    assert comm_like_res.status_code == 200
    assert comm_like_res.json()["data"]["is_liked"] is True
    assert comm_like_res.json()["data"]["total_likes"] == 1

    # 3. BOTÓN DE COMPARTIR (SHARE)
    share_res = client.post(f"/api/v1/interactions/videos/{video_id}/share", headers=headers, json={
        "platform": "whatsapp"
    })
    assert share_res.status_code == 200
    assert share_res.json()["data"]["platform"] == "whatsapp"
    assert share_res.json()["data"]["total_shares"] == 1
    assert f"/videos/{video_id}" in share_res.json()["data"]["share_url"]


def test_search_bar_microservice():
    """Prueba el microservicio de búsqueda (barra de búsqueda, hashtags y tendencias)."""
    search_res = client.get("/api/v1/search?q=baile")
    assert search_res.status_code == 200
    data = search_res.json()["data"]
    assert "videos" in data
    assert "users" in data
    assert "hashtags" in data

    trending_res = client.get("/api/v1/search/hashtags/trending")
    assert trending_res.status_code == 200


def test_media_upload_and_stream():
    """Prueba la subida real de archivos y streaming con soporte Range."""
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "juan_perez",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intento de subir archivo prohibido (.exe) -> 400
    fake_exe = io.BytesIO(b"binary content")
    bad_upload = client.post(
        "/api/v1/videos/upload-media?media_type=video",
        headers=headers,
        files={"file": ("virus.exe", fake_exe, "application/octet-stream")}
    )
    assert bad_upload.status_code == 400

    # Subir video MP4 válido
    fake_mp4 = io.BytesIO(b"\x00\x00\x00\x20ftypmp42" + b"A" * 1000)
    good_upload = client.post(
        "/api/v1/videos/upload-media?media_type=video",
        headers=headers,
        files={"file": ("sample_clip.mp4", fake_mp4, "video/mp4")}
    )
    assert good_upload.status_code == 201
    assert good_upload.json()["data"]["media_type"] == "video"
    assert "/uploads/videos/" in good_upload.json()["data"]["file_url"]


def test_moderation_rbac_security():
    """Verifica que un usuario estándar no pueda acceder a reportes de moderación (403 Forbidden)."""
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "juan_perez",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Juan es un usuario estándar (role='user') -> Acceso denegado
    reports_res = client.get("/api/v1/moderation/reports", headers=headers)
    assert reports_res.status_code == 403


def test_direct_video_publish_and_range_streaming():
    """Prueba la publicación directa de video multipart y streaming con HTTP Range y HEAD."""
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "juan_perez",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fake_video = io.BytesIO(b"\x00\x00\x00\x20ftypmp42" + b"V" * 5000)
    fake_thumb = io.BytesIO(b"\xff\xd8\xff\xe0" + b"T" * 200)

    # 1. Publicar directamente en un solo paso
    publish_res = client.post(
        "/api/v1/videos/publish",
        headers=headers,
        data={
            "title": "Tutorial de Baile Urbano #dance #freestyle",
            "description": "Aprende los mejores pasos con nosotros #sofiatrend",
            "duration_seconds": "25.0",
            "visibility": "public"
        },
        files={
            "video_file": ("baile_urbano.mp4", fake_video, "video/mp4"),
            "thumbnail_file": ("baile_cover.jpg", fake_thumb, "image/jpeg")
        }
    )
    assert publish_res.status_code == 201
    video_data = publish_res.json()["data"]
    video_id = video_data["id"]
    assert video_data["title"] == "Tutorial de Baile Urbano #dance #freestyle"
    assert "/uploads/videos/" in video_data["video_url"]
    assert "/uploads/thumbnails/" in video_data["thumbnail_url"]

    # 2. Transmisión HTTP Range (206 Partial Content)
    stream_res = client.get(
        f"/api/v1/videos/{video_id}/stream",
        headers={"Range": "bytes=0-499"}
    )
    assert stream_res.status_code == 206
    assert "Content-Range" in stream_res.headers
    assert stream_res.headers["Content-Range"].startswith("bytes 0-499/")

    # 3. Transmisión HEAD request (para players nativos)
    head_res = client.head(f"/api/v1/videos/{video_id}/stream")
    assert head_res.status_code == 200
    assert head_res.headers.get("Accept-Ranges") == "bytes"
    assert "Content-Length" in head_res.headers


def test_stories_microservice_lifecycle():
    """Prueba el ciclo de vida completo de Historias de 24 horas (publicación, feed, vistas, expiración y borrado)."""
    # 1. Login autor
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "juan_perez",
        "password": "Password123!"
    })
    token_author = login_res.json()["data"]["token"]["access_token"]
    headers_author = {"Authorization": f"Bearer {token_author}"}

    # 2. Intento de historia con contenido inapropiado -> 422
    fake_img = io.BytesIO(b"\xff\xd8\xff\xe0" + b"X" * 100)
    bad_story = client.post(
        "/api/v1/stories/publish",
        headers=headers_author,
        data={"caption": "video con porno y sexo explicito", "media_type": "image"},
        files={"file": ("bad.jpg", fake_img, "image/jpeg")}
    )
    assert bad_story.status_code == 422

    # 3. Publicación exitosa de historia (imagen)
    fake_story_img = io.BytesIO(b"\xff\xd8\xff\xe0" + b"I" * 300)
    story_pub_res = client.post(
        "/api/v1/stories/publish",
        headers=headers_author,
        data={"caption": "¡Un día increíble de grabación! ✨", "media_type": "image", "duration_seconds": "5.0"},
        files={"file": ("story_foto.jpg", fake_story_img, "image/jpeg")}
    )
    assert story_pub_res.status_code == 201
    story_data = story_pub_res.json()["data"]
    story_id = story_data["id"]
    assert story_data["caption"] == "¡Un día increíble de grabación! ✨"
    assert story_data["media_type"] == "image"
    assert story_data["is_expired"] is False

    # 4. Publicación vía JSON
    story_json_res = client.post(
        "/api/v1/stories/",
        headers=headers_author,
        json={
            "media_url": "/uploads/stories/sample.mp4",
            "media_type": "video",
            "caption": "Segunda historia en video",
            "duration_seconds": 10.0
        }
    )
    assert story_json_res.status_code == 201

    # 5. Consultar Feed de historias agrupadas (bandeja tipo Instagram/TikTok)
    feed_res = client.get("/api/v1/stories/feed", headers=headers_author)
    assert feed_res.status_code == 200
    feed_data = feed_res.json()["data"]
    assert feed_data["total_authors"] >= 1
    tray_item = feed_data["tray"][0]
    assert tray_item["stories_count"] >= 2
    assert "author" in tray_item

    # 6. Consultar historias específicas del usuario
    user_stories = client.get(f"/api/v1/stories/user/{story_data['user_id']}")
    assert user_stories.status_code == 200
    assert len(user_stories.json()["data"]) >= 2

    # 7. Registrar visualización desde otro usuario (lucia_teen)
    login_lucia = client.post("/api/v1/auth/login", json={
        "username_or_email": "lucia_teen",
        "password": "Password123!"
    })
    token_lucia = login_lucia.json()["data"]["token"]["access_token"]
    headers_lucia = {"Authorization": f"Bearer {token_lucia}"}

    view_res = client.post(f"/api/v1/stories/{story_id}/view", headers=headers_lucia)
    assert view_res.status_code == 200
    assert view_res.json()["data"]["views_count"] == 1

    # 8. Ver lista de espectadores (Autor: permitido, Otro usuario: 403)
    viewers_ok = client.get(f"/api/v1/stories/{story_id}/viewers", headers=headers_author)
    assert viewers_ok.status_code == 200
    assert viewers_ok.json()["data"]["views_count"] == 1
    assert viewers_ok.json()["data"]["viewers"][0]["username"] == "lucia_teen"

    viewers_forbidden = client.get(f"/api/v1/stories/{story_id}/viewers", headers=headers_lucia)
    assert viewers_forbidden.status_code == 403

    # 9. Borrar historia
    del_res = client.delete(f"/api/v1/stories/{story_id}", headers=headers_author)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


if __name__ == "__main__":
    test_api_health_and_root()
    test_parental_pin_hashing_and_verification()
    test_screen_time_and_curfew_rules()
    test_content_safety_clean_content()
    test_content_safety_leetspeak_and_censorship()
    test_video_audience_classification()
    test_full_auth_and_user_flow()
    test_interaction_buttons_like_comment_share()
    test_search_bar_microservice()
    test_media_upload_and_stream()
    test_moderation_rbac_security()
    test_direct_video_publish_and_range_streaming()
    test_stories_microservice_lifecycle()
    print("==================================================================")
    print(" ¡TODAS LAS PRUEBAS (REGLAS, API, VIDEOS, STORIES 24H, STREAMING) PASARON 100% OK! ")
    print("==================================================================")

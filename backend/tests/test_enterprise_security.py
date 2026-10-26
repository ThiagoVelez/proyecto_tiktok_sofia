"""
Pruebas Automatizadas de Infraestructura Robusta y Seguridad Empresarial
Proyecto Sofía - Plataforma TikTok-like
Cubre: Cabeceras de seguridad, Request ID, Refresh Tokens, Token Blocklist/Logout,
Validación de Magic Bytes, Health Check Profundo, Métricas Prometheus y Rate Limiting.
"""

import sys
import io
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Asegurar raíz en PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.core.database import Base, get_db, UserModel
from backend.core.security import hash_password, is_token_revoked
from backend.main import app

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


def test_security_headers_and_request_id():
    """Verifica la presencia obligatoria de cabeceras de seguridad OWASP y trazabilidad."""
    response = client.get("/")
    assert response.status_code == 200

    # Cabeceras de seguridad
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")

    # Trazabilidad
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers


def test_deep_health_check_and_metrics():
    """Verifica que el endpoint /health realice inspección real de BD y almacenamiento, y /metrics responda."""
    health_res = client.get("/health")
    assert health_res.status_code == 200
    data = health_res.json()["data"]
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data["components"]
    assert data["components"]["database"]["status"] == "up"
    assert "storage" in data["components"]
    assert data["components"]["storage"]["status"] == "up"

    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    assert "sofia_app_info" in metrics_res.text


def test_refresh_token_and_logout_revocation_cycle():
    """Prueba el ciclo de vida completo de autenticación: Login, Refresh Token Rotation y Logout con revocación."""
    # 1. Registro de usuario de prueba
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "usuario_seguridad",
        "email": "seguridad@test.com",
        "password": "PasswordSegura123!",
        "full_name": "Auditor de Seguridad",
        "birth_date": "1998-05-10"
    })
    assert reg_res.status_code == 201
    auth_data = reg_res.json()["data"]
    access_token = auth_data["token"]["access_token"]
    refresh_token = auth_data["token"]["refresh_token"]

    assert access_token is not None
    assert refresh_token is not None

    # 2. Acceso autenticado exitoso
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["username"] == "usuario_seguridad"

    # 3. Rotación de tokens con /auth/refresh
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_auth_data = refresh_res.json()["data"]
    new_access_token = new_auth_data["token"]["access_token"]
    new_refresh_token = new_auth_data["token"]["refresh_token"]

    assert new_access_token != access_token
    assert new_refresh_token != refresh_token

    # 4. Intento de reutilizar el Refresh Token anterior -> 401 (ya revocado)
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert replay_res.status_code == 401

    # 5. Logout y revocación de sesión
    logout_res = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {new_access_token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["data"]["revoked"] is True

    # 6. Intento de acceder con el token revocado -> 401 Unauthorized
    revoked_access_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    resp_body = revoked_access_res.json()
    err_text = str(resp_body.get("detail", "")) + str(resp_body.get("message", ""))
    assert "revocado" in err_text.lower()


def test_magic_bytes_security_rejection():
    """Verifica que archivos con extensión válida pero contenido binario no coincidente sean rechazados."""
    # Login para obtener credencial
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "usuario_seguridad",
        "password": "PasswordSegura123!"
    })
    token = login_res.json()["data"]["token"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Archivo con extensión .mp4 pero contenido que NO es video (ej: texto plano o script malicioso)
    fake_malicious_script = io.BytesIO(b"#!/bin/bash\necho 'payload_ataque'\n")
    bad_res = client.post(
        "/api/v1/videos/upload-media?media_type=video",
        headers=headers,
        files={"file": ("malicious.mp4", fake_malicious_script, "video/mp4")}
    )
    assert bad_res.status_code == 400
    assert "firma binaria" in bad_res.json()["detail"].lower()

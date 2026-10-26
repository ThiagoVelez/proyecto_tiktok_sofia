from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database import get_db, UserModel
from backend.core.security import get_current_user, require_roles
from backend.core.response import ApiResponse
from .schemas import ReportCreateRequest, ReportResponse, ModActionRequest, ModerationAuditResponse
from .service import ModerationService

router = APIRouter(prefix="/moderation", tags=["Moderación y Seguridad de la Comunidad"])


@router.post("/reports", response_model=ApiResponse[ReportResponse], status_code=status.HTTP_201_CREATED)
def submit_report(
    req: ReportCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permite a cualquier usuario autenticado denunciar videos, comentarios o perfiles inapropiados."""
    service = ModerationService(db)
    report = service.submit_report(current_user, req)
    return ApiResponse.success_response(data=report, message="Denuncia recibida y enviada a revisión.")


@router.get("/reports", response_model=ApiResponse[List[ReportResponse]])
def list_reports(
    status_filter: Optional[str] = Query(None, description="pending, under_review, resolved_action_taken, dismissed"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    moderator: UserModel = Depends(require_roles(["moderator", "admin"])),
    db: Session = Depends(get_db)
):
    """Consulta la cola de reportes pendientes (exclusivo para moderadores y administradores)."""
    service = ModerationService(db)
    reports = service.list_reports(status_filter=status_filter, limit=limit, offset=offset)
    return ApiResponse.success_response(data=reports, message="Lista de reportes obtenida.")


@router.post("/reports/{report_id}/resolve", response_model=ApiResponse[dict])
def resolve_report(
    report_id: int,
    req: ModActionRequest,
    moderator: UserModel = Depends(require_roles(["moderator", "admin"])),
    db: Session = Depends(get_db)
):
    """Resuelve un reporte aplicando la sanción correspondiente (exclusivo para moderadores y administradores)."""
    service = ModerationService(db)
    res = service.resolve_report(moderator, report_id, req)
    return ApiResponse.success_response(data=res, message=res["message"])


@router.get("/audits", response_model=ApiResponse[List[ModerationAuditResponse]])
def get_moderation_audits(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    moderator: UserModel = Depends(require_roles(["moderator", "admin"])),
    db: Session = Depends(get_db)
):
    """Consulta el historial de auditoría de las reglas automáticas ejecutadas (exclusivo para moderadores y admins)."""
    service = ModerationService(db)
    audits = service.get_audit_trail(limit=limit, offset=offset)
    return ApiResponse.success_response(data=audits, message="Registro de auditoría obtenido.")


from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from backend.core.database import ContentReportModel, ModerationAuditModel, VideoModel, CommentModel, UserModel
from .schemas import ReportCreateRequest, ReportResponse, ModActionRequest, ModerationAuditResponse


class ModerationService:
    def __init__(self, db: Session):
        self.db = db

    def submit_report(self, reporter: UserModel, req: ReportCreateRequest) -> ReportResponse:
        report = ContentReportModel(
            reporter_user_id=reporter.id,
            target_type=req.target_type,
            target_id=req.target_id,
            reason_category=req.reason_category,
            details=req.details,
            status="pending"
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return ReportResponse(
            id=report.id,
            reporter_user_id=report.reporter_user_id,
            target_type=report.target_type,
            target_id=report.target_id,
            reason_category=report.reason_category,
            details=report.details,
            status=report.status,
            created_at=report.created_at
        )

    def list_reports(self, status_filter: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[ReportResponse]:
        query = self.db.query(ContentReportModel)
        if status_filter:
            query = query.filter(ContentReportModel.status == status_filter)

        reports = query.order_by(desc(ContentReportModel.created_at)).offset(offset).limit(limit).all()
        return [
            ReportResponse(
                id=r.id,
                reporter_user_id=r.reporter_user_id,
                target_type=r.target_type,
                target_id=r.target_id,
                reason_category=r.reason_category,
                details=r.details,
                status=r.status,
                created_at=r.created_at
            ) for r in reports
        ]

    def resolve_report(self, moderator: UserModel, report_id: int, req: ModActionRequest) -> dict:
        report = self.db.query(ContentReportModel).filter(ContentReportModel.id == report_id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado.")

        # Aplicar acción sobre el recurso
        if req.action == "hide_content":
            if report.target_type == "video":
                video = self.db.query(VideoModel).filter(VideoModel.id == report.target_id).first()
                if video:
                    video.moderation_status = "hidden"
            elif report.target_type == "comment":
                comm = self.db.query(CommentModel).filter(CommentModel.id == report.target_id).first()
                if comm:
                    comm.moderation_status = "hidden"
            report.status = "resolved_action_taken"

        elif req.action == "ban_content":
            if report.target_type == "video":
                video = self.db.query(VideoModel).filter(VideoModel.id == report.target_id).first()
                if video:
                    video.moderation_status = "banned"
            report.status = "resolved_action_taken"

        elif req.action == "dismiss":
            report.status = "dismissed"

        report.moderator_notes = req.moderator_notes
        report.resolved_by_user_id = moderator.id
        report.resolved_at = datetime.now(timezone.utc)
        self.db.commit()

        return {"message": f"Reporte #{report_id} resuelto con estado '{report.status}'"}

    def get_audit_trail(self, limit: int = 50, offset: int = 0) -> List[ModerationAuditResponse]:
        audits = self.db.query(ModerationAuditModel).order_by(
            desc(ModerationAuditModel.created_at)
        ).offset(offset).limit(limit).all()

        return [
            ModerationAuditResponse(
                id=a.id,
                target_type=a.target_type,
                target_id=a.target_id,
                rule_triggered=a.rule_triggered,
                severity_level=a.severity_level,
                action_applied=a.action_applied,
                reason=a.reason,
                evaluated_text_snippet=a.evaluated_text_snippet,
                created_at=a.created_at
            ) for a in audits
        ]

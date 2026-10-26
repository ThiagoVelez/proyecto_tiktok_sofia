"""
Excepciones de dominio y manejadores de error de la plataforma.
"""

from fastapi import HTTPException, status


class SofiaBaseException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "ERROR"):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class ParentalRestrictionException(SofiaBaseException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PARENTAL_CONTROL_RESTRICTION"
        )


class ContentSafetyException(SofiaBaseException):
    def __init__(self, detail: str, violations: list = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="CONTENT_SAFETY_VIOLATION"
        )
        self.violations = violations or []


class EntityNotFoundException(SofiaBaseException):
    def __init__(self, entity_name: str, entity_id: any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} con identificador {entity_id} no fue encontrado.",
            error_code="NOT_FOUND"
        )

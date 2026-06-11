from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import ApplicationStatus
from app.schemas.base import ORMBase


class ApplicationCreate(BaseModel):
    customer_id: str
    merchant_id: str
    amount: float = Field(gt=0, le=50_000)
    term_months: int = Field(ge=1, le=36)


class ApplicationDecision(BaseModel):
    status: ApplicationStatus = Field(
        description="Only APPROVED or REJECTED allowed"
    )
    rejection_reason: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "APPROVED",
                "rejection_reason": None,
            }
        }
    }


class ApplicationResponse(ORMBase):
    id: str
    customer_id: str
    merchant_id: str
    requested_amount: float
    requested_term_months: int
    status: ApplicationStatus
    rejection_reason: str | None
    credit_score_at_application: int | None
    created_at: datetime

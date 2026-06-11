from datetime import datetime

from pydantic import BaseModel
from app.schemas.base import ORMBase


from app.core.enums import LoanStatus


class LoanResponse(ORMBase):
    id: str
    application_id: str
    customer_id: str
    merchant_id: str
    principal_amount: float
    interest_rate: float
    term_months: int
    status: LoanStatus
    disbursed_at: datetime
    closed_at: datetime | None

from datetime import date, datetime

from pydantic import BaseModel
from app.schemas.base import ORMBase


from app.core.enums import InstallmentStatus


class InstallmentResponse(ORMBase):
    id: str
    installment_number: int
    due_date: date
    principal_portion: float
    interest_portion: float
    total_amount: float
    status: InstallmentStatus
    paid_at: datetime | None
    overdue_days: int



class LoanScheduleResponse(BaseModel):
    loan_id: str
    principal_amount: float
    total_payable: float
    installments: list[InstallmentResponse]
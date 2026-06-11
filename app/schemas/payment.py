from datetime import datetime

from pydantic import BaseModel, Field
from app.schemas.base import ORMBase

from app.core.enums import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    payment_method: PaymentMethod
    provider_transaction_id: str | None = Field(
        default=None,
        description="External payment provider reference",
    )


class PaymentResponse(ORMBase):
    id: str
    installment_id: str
    amount: float
    status: PaymentStatus
    payment_method: PaymentMethod
    provider_transaction_id: str | None
    created_at: datetime

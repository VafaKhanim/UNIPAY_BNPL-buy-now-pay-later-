from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentMethod, PaymentStatus
from app.models.base import BaseModel


class Payment(BaseModel):
    __tablename__ = "payments"

    installment_id: Mapped[str] = mapped_column(
        ForeignKey("installments.id"), index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.PENDING)
    payment_method: Mapped[str] = mapped_column(String(20))
    provider_transaction_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True
    )

    installment: Mapped["Installment"] = relationship(back_populates="payments")  # noqa: F821
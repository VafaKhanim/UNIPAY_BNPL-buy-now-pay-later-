from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import InstallmentStatus
from app.models.base import BaseModel


class Installment(BaseModel):
    __tablename__ = "installments"

    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"), index=True)
    installment_number: Mapped[int] = mapped_column(Integer)
    due_date: Mapped[date] = mapped_column(Date)
    principal_portion: Mapped[float] = mapped_column(Numeric(12, 2))
    interest_portion: Mapped[float] = mapped_column(Numeric(12, 2))
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(
        String(20), default=InstallmentStatus.SCHEDULED
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    overdue_days: Mapped[int] = mapped_column(Integer, default=0)

    loan: Mapped["Loan"] = relationship(back_populates="installments")  # noqa: F821
    payments: Mapped[list["Payment"]] = relationship(back_populates="installment")  # noqa: F821
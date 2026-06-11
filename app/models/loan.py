from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ApplicationStatus, LoanStatus
from app.models.base import BaseModel


class LoanApplication(BaseModel):
    __tablename__ = "loan_applications"

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"))
    requested_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    requested_term_months: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20), default=ApplicationStatus.PENDING
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    credit_score_at_application: Mapped[int | None] = mapped_column(nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="applications")  # noqa: F821
    merchant: Mapped["Merchant"] = relationship(back_populates="applications")  # noqa: F821
    loan: Mapped["Loan | None"] = relationship(back_populates="application")


class Loan(BaseModel):
    __tablename__ = "loans"

    application_id: Mapped[str] = mapped_column(
        ForeignKey("loan_applications.id"), unique=True
    )
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"))
    principal_amount: Mapped[float] = mapped_column(Numeric(12, 2))
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 4))
    term_months: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default=LoanStatus.ACTIVE)
    disbursed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    application: Mapped["LoanApplication"] = relationship(back_populates="loan")
    customer: Mapped["Customer"] = relationship(back_populates="loans")  # noqa: F821
    installments: Mapped[list["Installment"]] = relationship(  # noqa: F821
        back_populates="loan", order_by="Installment.installment_number"
    )
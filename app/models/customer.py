from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import KYCStatus
from app.models.base import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"

    full_name: Mapped[str] = mapped_column(String(255))
    national_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    kyc_status: Mapped[str] = mapped_column(
        String(20), default=KYCStatus.PENDING
    )
    credit_score: Mapped[int | None] = mapped_column(nullable=True)

    applications: Mapped[list["LoanApplication"]] = relationship(  # noqa: F821
        back_populates="customer"
    )
    loans: Mapped[list["Loan"]] = relationship(back_populates="customer")  # noqa: F821
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Merchant(BaseModel):
    __tablename__ = "merchants"

    business_name: Mapped[str] = mapped_column(String(255))
    tax_id: Mapped[str] = mapped_column(String(50), unique=True)
    settlement_iban: Mapped[str] = mapped_column(String(34))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    applications: Mapped[list["LoanApplication"]] = relationship(  # noqa: F821
        back_populates="merchant"
    )
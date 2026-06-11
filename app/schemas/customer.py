from pydantic import BaseModel, EmailStr, Field

from app.core.enums import KYCStatus
from app.schemas.base import ORMBase


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    national_id: str = Field(min_length=5, max_length=50)
    phone: str = Field(pattern=r"^\+?[0-9]{9,15}$")
    email: EmailStr


class CustomerKYCUpdate(BaseModel):
    kyc_status: KYCStatus
    credit_score: int | None = Field(default=None, ge=0, le=1000)


class CustomerResponse(ORMBase):
    id: str
    full_name: str
    phone: str
    email: str
    kyc_status: KYCStatus
    credit_score: int | None
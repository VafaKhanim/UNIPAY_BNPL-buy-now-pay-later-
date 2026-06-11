from pydantic import BaseModel, Field
from app.schemas.base import ORMBase



class MerchantCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=255)
    tax_id: str = Field(min_length=5, max_length=50)
    settlement_iban: str = Field(min_length=15, max_length=34)


class MerchantStatusUpdate(BaseModel):
    is_active: bool


class MerchantResponse(ORMBase):
    id: str
    business_name: str
    tax_id: str
    settlement_iban: str
    is_active: bool

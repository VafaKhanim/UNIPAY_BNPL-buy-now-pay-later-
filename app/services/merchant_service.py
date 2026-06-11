from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateError, NotFoundError
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantStatusUpdate


class MerchantService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MerchantCreate) -> Merchant:
        if self.db.query(Merchant).filter_by(tax_id=data.tax_id).first():
            raise DuplicateError("tax_id")
        merchant = Merchant(
            business_name=data.business_name,
            tax_id=data.tax_id,
            settlement_iban=data.settlement_iban,
        )
        self.db.add(merchant)
        self.db.commit()
        self.db.refresh(merchant)
        return merchant

    def get_by_id(self, merchant_id: str) -> Merchant:
        merchant = self.db.get(Merchant, merchant_id)
        if not merchant:
            raise NotFoundError("Merchant", merchant_id)
        return merchant

    def update_status(self, merchant_id: str, data: MerchantStatusUpdate) -> Merchant:
        merchant = self.get_by_id(merchant_id)
        merchant.is_active = data.is_active
        self.db.commit()
        self.db.refresh(merchant)
        return merchant
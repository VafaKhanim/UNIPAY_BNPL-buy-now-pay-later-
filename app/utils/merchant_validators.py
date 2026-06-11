from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.merchant import Merchant


def get_active_merchant(db: Session, merchant_id: str) -> Merchant:
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise NotFoundError("Merchant", merchant_id)
    if not merchant.is_active:
        raise BusinessRuleError("Merchant is not active")
    return merchant
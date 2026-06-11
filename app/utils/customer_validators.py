from sqlalchemy.orm import Session

from app.core.enums import KYCStatus
from app.core.exceptions import BusinessRuleError, DuplicateError, NotFoundError
from app.models.customer import Customer


def get_verified_customer(db: Session, customer_id: str) -> Customer:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise NotFoundError("Customer", customer_id)
    if customer.kyc_status != KYCStatus.VERIFIED:
        raise BusinessRuleError("Customer KYC is not verified")
    return customer


def assert_unique_customer_fields(
    db: Session, national_id: str, phone: str, email: str
) -> None:
    exists = (
        db.query(Customer)
        .filter(
            (Customer.national_id == national_id)
            | (Customer.phone == phone)
            | (Customer.email == email)
        )
        .first()
    )
    if exists:
        raise DuplicateError("national_id, phone, or email")



